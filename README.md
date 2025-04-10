# MIMIC-IV-Ext-DiReCT
This README provides an introductory overview of the DiReCT dataset. The dataset is organized into two .rar files: **diagnostic_kg.rar**, which contains all the knowledge graphs, and **samples.rar**, which includes 511 annotated notes. Below, we outline the basic usage of these files. 
For detailed implementation instructions and experimental code, please refer to our GitHub repository: https://github.com/wbw520/DiReCT.

## Knowledge Graphs
The knowledge graph for each disease category is saved as a JSON file in the unzipped "diagnostic_kg" folder as following:
```
-diagnostic_kg
    - Disease Category 1.json
    - Disease Category 2.json
    - Disease Category 3.json
    ...
```
Key of "diagnostic" represent the diagnostic procedure (in a tree structure), from a diagnosis of suspected a disease to the final diagnosis. Key of "knowledge" records the premises for each diagnosis. Note that each premise is separated with ";".

A subgraph sample for Heart Failure is shown as following:
```
{"diagnostic": 
    {"Suspected Heart Failure": 
        {"Strongly Suspected Heart Failure": 
            {"Heart Failure": 
                {"HFrEF": [], 
                 "HFmrEF": [], 
                 "HFpEF": []}}}},
"knowledge": 
    {"Suspected Heart Failure": 
        {"Risk Factors": "CAD; Hypertension; Valve disease; Arrhythmias; CMPs; Congenital heart disease, Infective; Drug-induced; Infiltrative; Storage disorders; Endomyocardial disease; Pericardial disease; Metabolic; Neuromuscular disease; etc.", 
         "Symptoms": "Breathlessness; Orthopnoea; Paroxysmal nocturnal dyspnoea; Reduced exercise tolerance; Fatigue; tiredness; increased time to recover after exercise; Ankle swelling; Nocturnal cough; Wheezing; Bloated feeling; Loss of appetite; Confusion (especially in the elderly); Depression; Palpitation; Dizziness; Syncope.; etc.", 
         "Signs": "Elevated jugular venous pressure; Hepatojugular reflux; Third heart sound (gallop rhythm); Laterally displaced apical impulse; Weight gain (>2 kg/week); Weight loss (in advanced HF); Tissue wasting (cachexia); Cardiac murmur; Peripheral edema (ankle, sacral, scrotal); Pulmonary crepitations; Pleural effusion; Tachycardia; Irregular pulse; Tachypnoea; Cheyne-Stokes respiration; Hepatomegaly; Ascites; Cold extremities; Oliguria;  Narrow pulse pressure."}, 
     "Strongly Suspected Heart Failure": "NT-proBNP > 125 pg/mLor BNP > 35 pg/mL\n", 
     "Heart Failure": "Abnormal findings from echocardiography:LV mass index ≥ 95 g/m2 (Female), ≥ 115 g/m2 (Male); Relative wall thickness >0.42, LA volume index>34 mL/m2, E/e' ratio at rest >9, PA systolic pressure >35 mmHg; TR velocity at rest >2.8 m/s, etc.", 
     "HFrEF": "LVEF<40%", 
     "HFmrEF": "LVEF41~49%", 
     "HFpEF": "LVEF>50%"}}
```

## Annotated Data
We store the annotated notes as JSON files and saved in folders named after the disease categories and primary discharge diagnosis (PDD). Each JSON file record the annotated diagnostic procedure for a PDD. 
After unzipping the samples.rar file, the data is formulated as following:
```
-samples
    - Disease Category 1
          - PDD Category 1
                 - note_1.json
                 - note_2.json
                 - note_3.json
                 ...
          - PDD Category 2
          ...
    - Disease Category 2
    - Disease Category 3
    ...
```
We also provided a [Data List](https://github.com/wbw520/DiReCT/blob/master/utils/data_loading_analysisi/data_list.csv) for detailed structure information. For reading a JSON file, you can use the [Annotation Tool](https://github.com/wbw520/DiReCT/tree/master/utils/data_annotation) to visualize it.
Here we also demonstrate the code to load a JSON (refer to GitHub repository). It will process an annotated JSON file and reconstructed it with a tree structure. 
```
from utils.data_analysis import cal_a_json, deduction_assemble

root = "samples/Stroke/Hemorrhagic Stroke/sample1.json"
record_node, input_content, chain = cal_a_json(root)
```
record_node: A dictionary for all nodes in our annotation with node index as key. Each node is also saved as a dictionary where <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"content" record the content of the node. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"type" show the node annotation type, e.g., "Input" as observations, "Cause" as rationale, and "Intermedia" as diagnosis. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"connection" gives the children node's key (if no child, it is the leaf diagnostic node). <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"upper" gives the parent node's key (if no parent, it is the observation node). <br>
input_content: A dictionary saves original clinical note from "input1"-"Chief Complaint" to "input6"-"Pertinent Results" <br>
chain: A list structure saves the diagnostic procedure in order (from suspected to one PDD).
```
GT = deduction_assemble(record_node)
```
deduction_assemble() organizes all nodes and return the all deductions as {o: [z,r,d]...}.  <br>
 <br>
o: extracted disease observation from raw text. <br>
d: name of the diagnosis. <br>
z: the rationale to explain why an observation can be related to a diagnosis d. <br>
r: the part (from one of input1-6) of the clinical note where o is extracted.