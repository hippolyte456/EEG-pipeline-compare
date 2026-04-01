# --- hemiano - SUB 1 - brainvision
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.eeg 
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.json 
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.vhdr 
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.vmrk

# --- hemiano - SUB 1 - Neurolectrics
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-02/eeg/sub-0001_ses-02_task-rest_acq-post_run-1_eeg.easy 
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-02/eeg/sub-0001_ses-02_task-rest_acq-pre_run-1_eeg.info 

# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-02/eeg/sub-0001_ses-02_task-rest_acq-post_run-1_eeg.info 
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-02/eeg/sub-0001_ses-02_task-rest_acq-pre_run-1_eeg.easy


# --- hemiano - SUB 2 - brainvision
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0002/ses-01/eeg/sub-0002_ses-01_task-rest_acq-EC_run-1_eeg.eeg
# /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0002/ses-01/eeg/sub-0002_ses-01_task-rest_acq-EO_run-1_eeg.eeg

# --- hemiano - SUB 2 - Neurolectrics
# ...same for clonesa



cd /Users/hippolyte.dreyfus/Documents/EEG-pipeline-compare/eeg-pipeline-compare

# BrainVision: pass the .vhdr (or any companion .eeg / .vmrk — the .vhdr is resolved automatically)
python run.py \
  --a /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.vhdr \
  --b /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0002/ses-01/eeg/sub-0002_ses-01_task-rest_acq-EC_run-1_eeg.vhdr \
  --out result.json

# # Alternative: pass the .eeg companion directly (same result)
# python run.py \
#   --a /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0001/ses-01/eeg/sub-0001_ses-01_task-detection_run-1_eeg.eeg \
#   --b /Volumes/levy/raw/valerocabre/hemianotACS/Data/derivatives/bids/sub-0002/ses-01/eeg/sub-0002_ses-01_task-rest_acq-EC_run-1_eeg.eeg \
#   --out result.json