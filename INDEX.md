# WORKSPACE INDEX

## Directory Tree
```text
├── .devcontainer
│   ├── devcontainer.json
│   └── icon.svg
├── .github
│   └── workflows
│       ├── ci.yml
│       └── index.yml
├── .gui_runs
│   └── .gitkeep
├── .ndjson
│   └── .gitkeep
├── app
│   ├── __init__.py
│   ├── dep_cloud.py
│   ├── index_repo.py
│   ├── metrics.py
│   ├── orchestrator.py
│   ├── pipeline_gui.py
│   ├── run_pipeline.py
│   └── tdiff.py
├── configs
│   ├── agents.json
│   ├── agents.toml
│   ├── pipelines.json
│   └── pipelines.toml
├── data
│   └── atlantis.csv
├── docs
│   └── qsys_sbs_scss.md
├── notebooks
│   ├── image-classifier.ipynb
│   ├── matplotlib.ipynb
│   └── population.ipynb
├── output
│   └── handover_final
│       └── conversations_manifest.json
├── reports
│   └── .gitkeep
├── scripts
│   └── build_index.py
├── src
│   ├── master_doc_system
│   │   └── utils.py
│   ├── measure_phase
│   │   ├── parser
│   │   │   ├── __init__.py
│   │   │   ├── base_parser.py
│   │   │   ├── markdown_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── powerpoint_parser.py
│   │   │   ├── visio_parser.py
│   │   │   ├── word_parser.py
│   │   │   └── zip_parser.py
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── classifier.py
│   │   ├── index.py
│   │   ├── keb_interface.py
│   │   ├── metrics.py
│   │   ├── ranking.py
│   │   └── workflow.py
│   └── zip_pipeline.py
├── tests
│   ├── measure_phase
│   │   └── test_basic_functionality.py
│   ├── conftest.py
│   ├── test_utils.py
│   └── test_zip_pipeline.py
├── .gitignore
├── GLOBAL_index.json
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── README_MEASURE.md
├── requirements-dev.txt
└── requirements.txt
```

## Main Files (by size)
- `src/measure_phase/metrics.py` (25920 bytes)
- `src/measure_phase/workflow.py` (22734 bytes)
- `src/measure_phase/keb_interface.py` (18670 bytes)
- `src/measure_phase/ranking.py` (18547 bytes)
- `src/measure_phase/cache.py` (16116 bytes)
- `src/measure_phase/index.py` (11990 bytes)
- `src/measure_phase/parser/zip_parser.py` (10993 bytes)
- `src/measure_phase/parser/markdown_parser.py` (8982 bytes)
- `src/measure_phase/parser/powerpoint_parser.py` (8926 bytes)
- `src/measure_phase/parser/pdf_parser.py` (7810 bytes)
- `src/measure_phase/classifier.py` (7128 bytes)
- `src/measure_phase/parser/visio_parser.py` (6697 bytes)
- `src/measure_phase/parser/word_parser.py` (6678 bytes)
- `tests/measure_phase/test_basic_functionality.py` (4121 bytes)
- `src/measure_phase/parser/base_parser.py` (3401 bytes)
- `app/orchestrator.py` (3010 bytes)
- `src/zip_pipeline.py` (2930 bytes)
- `app/pipeline_gui.py` (2287 bytes)
- `app/index_repo.py` (1777 bytes)
- `scripts/build_index.py` (1593 bytes)

## Word Cloud (top tokens)
```text
                self : 657
              return : 320
                 str : 316
                 for : 294
                 def : 245
            metadata : 228
            artifact : 169
                 get : 165
                Dict : 162
              import : 157
                 Any : 142
           file_path : 136
              append : 115
                text : 113
                from : 111
              logger : 110
               score : 108
           artifacts : 106
       artifact_type : 103
                List : 102
                 len : 99
             content : 89
                True : 86
                 and : 84
                 not : 83
                with : 83
               error : 83
                Path : 74
            priority : 73
                file : 72
              except : 70
                 key : 69
             metrics : 69
                 try : 62
               files : 60
           Exception : 57
               entry : 57
                elif : 57
                else : 56
               False : 56
               Error : 53
             Extract : 52
                data : 52
              result : 51
                name : 51
            analysis : 51
                path : 49
           structure : 48
                time : 46
                info : 46
```
