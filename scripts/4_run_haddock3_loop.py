"""
Script to run HADDOCK3 scoring on all candidate complex structures
"""

import pandas as pd
import os, re, subprocess

## Load in the previously processed collection data
collection_df = pd.read_csv('../data/proteinbase_collection_nipah-binder-competition-all-submissions_processed.csv')

## HADDOCK3 scoring function
def haddock3_score(pdb_path:str) -> dict:

  repo_dir = r'C:\Users\Colby\Documents\GitHub\Nipah_Binder_Competition_Analyses'
  try:
    ## Run haddock3-score CLI
    command = ["haddock3-score", "--full", pdb_path]
    # docker_command = f"docker run -v {repo_dir}:/inputs --rm cford38/haddock:3-2024.10.0b6 haddock3-score --full {pdb_path}"
    # command = docker_command.split()

    sp_result = subprocess.run(command, capture_output=True, text=True, check=True)

    ## Parse result
    metrics = {}

    ## Extract HADDOCK score
    match = re.search(r"HADDOCK-score \(emscoring\) = ([\-\d\.]+)", sp_result.stdout)
    if match:
        metrics["score"] = float(match.group(1))

    ## Extract individual energy terms
    matches = re.findall(r"(\w+)=([\-\d\.]+)", sp_result.stdout)
    for key, value in matches:
        metrics[key] = float(value)

    ## Calculate total score
    metrics["total"] = metrics["vdw"] + metrics["elec"]

    ## Remove air
    del metrics["air"]

    return metrics

  except subprocess.CalledProcessError as e:
    print("HADDOCK3 Error occurred:", e.stderr)
    return {}
  

## Loop through each candidate and run the ipsae script
haddock_df = pd.DataFrame(
    columns=[
        'id',
        ]
    )

for idx, row in collection_df.iterrows():
    id = row['id']
    print(f"Running HADDOCK for: {id}")
    # pdb_path = f'/inputs/data/structures/{id}_boltz2_complex.pdb'
    pdb_path = f'/mnt/c/Users/Colby/Documents/GitHub/Nipah_Binder_Competition_Analyses/data/structures/{id}_boltz2_complex.pdb'


    print(f"Scoring PDB file at: {pdb_path}")

    haddock_dict = haddock3_score(pdb_path = pdb_path)
    haddock_df_row = pd.DataFrame([haddock_dict])
    haddock_df_row['id'] = id
    # print(haddock_dict)

    haddock_df = pd.concat([haddock_df, haddock_df_row], ignore_index=True)

haddock_df.to_csv('../data/haddock3_scores.csv', index=False)