package main

import (
	"encoding/json"
	"github.com/jinzhu/gorm"
	_"github.com/mattn/go-sqlite3"
	"io/ioutil"
	"net/http"
	"runtime"
	"strconv"
	"log"
	"fmt"
	"strings"
	"time"
)

type Sport struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}
type OutcomeType struct {
	Id        int     `json:"id"`
	Name      string  `json:"name"`
	Parameter float32 `json:"parameter" gorm:"-"`
	Code      string  `json:"code"`
	SportId   int     `json:"sport_id"`
}
type Outcome struct {
	Value         float32 `json:"v"`
	Parameter     float32 `json:"p"`
	OutcomeTypeId int     `json:"id"`
}
type Model struct {
	Id           int                  `json:"id"`
	SportId      int                  `json:"sport_id"`
	Description  string               `json:"description"`
	InputParams  []Parameter          `json:"params"`
	TablesStage1 map[int]*OutcomeTable `json:"stage1,omitempty"`
	TablesStage2 map[int]*OutcomeTable `json:"stage2,omitempty"`
}
type OutcomeTable struct {
	ParamsIds   []int       `json:"params"` // param that effect on the outcome
	OutcomeType *OutcomeType `json:"outcome_type"`
	Values      []float32   `json:"values"` // can be vary large, over million items
	OutParam    *Parameter   `json:"out_param"`
}
type Parameter struct {
	Id          int             `json:"id"`
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Type        int             `json:"type"`
	ValueMap    map[string]int `json:"map,omitempty"` // int represent of float value of outcome, example {1.01:1, 1.02:2 ...}
	VRange      int             `json:"range,omitempty"`
}

var db *gorm.DB
var models map[int]Model = make(map[int]Model)
var modelsMeta map[int]Model = make(map[int]Model)

const STATIC = "models/"

func main() {
	runtime.GOMAXPROCS(1) // 4 cores, input your number of cores
	var err error
	db, err = gorm.Open("sqlite3", "app.db")
	if err != nil {
		panic("failed to connect database")
	}
	defer db.Close()
	http.HandleFunc("/sports", Sports)
	http.HandleFunc("/outcomes", OutcomeTypes)
	http.HandleFunc("/models", Models)
	http.HandleFunc("/load/", LoadModel) // admin only
	http.HandleFunc("/delete/", DeleteModel)
	http.HandleFunc("/calculate/", Calculate)
	http.ListenAndServe(":3001", nil)
}
func Sports(rw http.ResponseWriter, request *http.Request) {
	var sports []Sport
	db.Find(&sports)
	result, _ := json.Marshal(sports)
	rw.Write(result)
}

func OutcomeTypes(rw http.ResponseWriter, request *http.Request) {
	var outcomes []OutcomeType
	db.Find(&outcomes)
	result, _ := json.Marshal(outcomes)
	rw.Write(result)
}

func Models(rw http.ResponseWriter, request *http.Request) {
	result, _ := json.Marshal(modelsMeta)
	rw.Write(result)
}

func Calculate(rw http.ResponseWriter, request *http.Request) {
	start := time.Now()
	modelId, _ := strconv.Atoi(strings.Split(request.URL.Path, "/")[2])
	params := strings.Split(request.URL.Query()["params"][0], ",")
	model, ok := models[modelId]
	if !ok {
		rw.WriteHeader(201)
		return
	}
	type HashedParam struct{ value, vRange int }
	var hashedParams map[int]HashedParam = make(map[int]HashedParam)
	for i := 0; i < len(params); i++ {
		option := model.InputParams[i]
		hashedParams[i] = HashedParam{option.ValueMap[params[i]], option.VRange}
	}
	outcomes := make([]Outcome, len(model.TablesStage1) + len(model.TablesStage2))
	var outcome_index int
	getValue := func(t *OutcomeTable) float32 {
		var hash int
		if len(t.ParamsIds) == 1 {
			hash = hashedParams[t.ParamsIds[0]].value
		} else {
			hash = hashForTwo(hashedParams[t.ParamsIds[0]].value,
				hashedParams[t.ParamsIds[1]].value,
				hashedParams[t.ParamsIds[0]].vRange,
				hashedParams[t.ParamsIds[1]].value)
		}
		return t.Values[hash]
	}
	for _, t := range model.TablesStage1 {
		value := getValue(t)
		if value == 0 {
			continue
		}
		outcomes[outcome_index] = Outcome{value, t.OutcomeType.Parameter, t.OutcomeType.Id}
		if t.OutParam != nil {
			key := strconv.FormatFloat(float64(value), 'f', -1, 32)
			hashedParams[t.OutParam.Id] = HashedParam{t.OutParam.ValueMap[key], t.OutParam.VRange}
		}
		outcome_index++
	}
	for _, t := range model.TablesStage2 {
		value := getValue(t)
		if value == 0 {
			continue
		}
		outcomes[outcome_index] = Outcome{value, t.OutcomeType.Parameter, t.OutcomeType.Id}
		outcome_index++
	}
	result, _ := json.Marshal(outcomes)
	rw.Write(result)
	end := time.Since(start)
	log.Printf("Calculated, model Id = %d. Duration: %s", modelId, end)
}

func LoadModel(rw http.ResponseWriter, request *http.Request) {
	rw.Write([]byte(strconv.FormatBool(loadModel(strings.Split(request.URL.Path, "/")[2]))))

}

func DeleteModel(rw http.ResponseWriter, request *http.Request) {
	id, _ := strconv.Atoi(strings.Split(request.URL.Path, "/")[2])
	delete(models, id)
	delete(modelsMeta, id)
	log.Printf("Model deleted, id = %d", id)
}

func loadModel(name string) bool {
	path := fmt.Sprintf("%s%s/%s.json", STATIC, name, name)
	b, err := ioutil.ReadFile(path) // just pass the file name
	if err != nil {
		log.Printf("Failed to load new model, no such file %s", path)
		return false
	}
	var model Model
	jsonErr := json.Unmarshal(b, &model) // very large operation
	if jsonErr != nil {
		log.Printf("Failed to parse  model %s", path)
		return false
	}
	models[model.Id] = model
	for _, t := range model.TablesStage1 {
		if len(t.Values) == 0 {
			v, _ := ioutil.ReadFile(STATIC + name + "/outcomes/" + t.OutcomeType.Code)
			json.Unmarshal(v, &t.Values)
		}
	}
	for _, t := range model.TablesStage2 {
		if len(t.Values) == 0 {
			v, _ := ioutil.ReadFile(STATIC + name + "/outcomes/" + t.OutcomeType.Code)
			json.Unmarshal(v, &t.Values)
		}
	}
	paramsMeta := make([]Parameter, len(model.InputParams))
	for i := range paramsMeta {
		paramsMeta[i].Id = model.InputParams[i].Id
		paramsMeta[i].Description = model.InputParams[i].Description
		paramsMeta[i].Name = model.InputParams[i].Name
	}
	modelMeta := Model{Id:model.Id, Description:model.Description, SportId:model.SportId, InputParams:paramsMeta}
	modelsMeta[model.Id] = modelMeta
	log.Printf("New model loaded, Id = %d", model.Id)
	return true
}

func hashForTwo(p1, p2, range1, range2 int) int {
	if range1 > range2 {
		return p2 * range1 + p1
	} else {
		return p1 * range2 + p2
	}
}