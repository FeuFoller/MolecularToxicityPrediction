import json

import joblib
import numpy as np
import streamlit as st

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator

MODEL_PATH = "models/nr-er morganrandomforest.joblib"
CONFIG_PATH = "models/model_config.json"

model = joblib.load(MODEL_PATH)

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

generator = GetMorganGenerator(
    radius=config["radius"],
    fpSize=config["n_bits"]
)

st.set_page_config(
    page_title="NR-ER Activity Predictor",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 NR-ER Activity Predictor")

st.markdown(
    """
    **Molecular toxicity prediction using machine learning**

    Enter a molecule's SMILES representation to estimate
    its probability of activity in the NR-ER assay.
    """
)

with st.sidebar:
    st.header("About the model")

    st.write(
        """
        This application uses a Random Forest classifier
        trained on Morgan molecular fingerprints.
        """
    )

    st.write("**Dataset:** Tox21")
    st.write("**Target:** NR-ER")
    st.write("**Fingerprint:** Morgan")
    st.write("**Radius:** 2")
    st.write("**Bits:** 2048")

smiles = st.text_input(
    "SMILES",
    placeholder="Example: CCO",
    help="Enter a valid SMILES molecular representation."
)

predict_button = st.button(
    "Predict NR-ER Activity",
    type="primary"
)

if predict_button:

    if not smiles.strip():
        st.warning("Please enter a SMILES string.")

    else:
        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            st.error(
                "Invalid SMILES. Please check the structure "
                "and try again."
            )

        else:
            fingerprint = generator.GetFingerprint(mol)

            X_new = np.array(
                fingerprint
            ).reshape(1, -1)

            probability = model.predict_proba(
                X_new
            )[0, 1]

            prediction = int(
                probability >= config["threshold"]
            )
            st.subheader("Prediction")

            if prediction == 1:
                st.error(
                    "Potential NR-ER activity detected"
                )
            else:
                st.success(
                    "Predicted NR-ER inactive"
                )
                mol_weight = Descriptors.MolWt(mol)
                logp = Descriptors.MolLogP(mol)
                tpsa = Descriptors.TPSA(mol)

                st.subheader("Molecular Properties")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                "Molecular Weight",
                f"{mol_weight:.1f}"
                )

                col2.metric(
                "LogP",
                f"{logp:.2f}"
                )

                col3.metric(
                "TPSA",
                f"{tpsa:.1f}"
                )
                    
                
            st.metric(
                "Probability of NR-ER activity",
                f"{probability:.1%}"
            )

            if probability >= 0.5:
                interpretation = (
                    "The model predicts the molecule as "
                    "NR-ER active at the configured threshold."
                )
            else:
                interpretation = (
                    "The model predicts the molecule as "
                    "NR-ER inactive at the configured threshold."
                )

            st.info(interpretation)

            st.divider()

st.caption(
    """
    **Disclaimer:** This application predicts activity in the
    NR-ER assay based on a machine-learning model. It is not a
    clinical, diagnostic, or regulatory toxicity assessment.
    Predictions should not be used as a substitute for experimental
    testing or professional scientific judgment.
    """
)