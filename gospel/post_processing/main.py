from pathlib import Path
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import json
import os
import pandas as pd


folder = "../../outcomes-n7-good"
threshold_values = sorted([1])


bqp_error=0.4
with Path("../../circuits/table.json").open() as f:
    table = json.load(f)
    circuits = [name for name, prob in table.items() if prob < bqp_error or prob > 1-bqp_error]
    # prob = prob of having 1
    # prob < $bqp_error$ => No instance
    # print(len(circuits))

def find_correct_value(circuit_name):
    with Path("../../circuits/table.json").open() as f:
        table = json.load(f)
        # return 1 if yes instance
        # return 0 else (no instance, as circuits are already filtered)
        # print(table[circuit_name])
        return(int(table[circuit_name] > 1-bqp_error))



files_dict = {}
for file in os.listdir(folder):
    file_path=os.path.join(folder, file)
    if "raw" not in file_path:
        prob = file.split(".json")[0].split("p")[1]
        files_dict[prob] = file_path
    

def get_failure_rate(threshold:float):
    proportion_wrong_outcomes_dict = {}
    for prob in files_dict:
        file_path = files_dict[prob]
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        # Convert JSON data to DataFrame
        df = pd.DataFrame.from_dict(json_data, orient='index')
        df["expected_outcome"] = [find_correct_value(circuit) for circuit in df.index]

        proportion_wrong_outcomes = len(df[(df['outcome'] != "Ambig.") & (df['outcome'] != df["expected_outcome"]) & (df['failure_rate'] < threshold)])/len(df)
        print(prob)
        print(df[(df['outcome'] != "Ambig.") & (df['outcome'] != df["expected_outcome"]) & (df['failure_rate'] < threshold)])
            
        proportion_wrong_outcomes_dict[prob] = proportion_wrong_outcomes
    return proportion_wrong_outcomes_dict

p_values = sorted(list(files_dict.keys()))

filename = "wrong-decisions-prob.csv"

# Open the file for writing
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    
    # Write header row
    writer.writerow(["Threshold"] + p_values)
    
    # Compute and write failure rates
    for t in threshold_values:
        proportion_wrong_outcomes_dict = get_failure_rate(t)
        comp_failure_rates = [proportion_wrong_outcomes_dict[prob] for prob in p_values]
        print(comp_failure_rates)
        writer.writerow([t] + comp_failure_rates)

print(f"Data saved to {filename}")