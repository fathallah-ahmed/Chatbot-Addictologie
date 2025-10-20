
"""
FICHIER : fine_tuning_lora.py (Script d'entraînement LoRA)
STATUT : EXPÉRIMENTAL - Préparation pour futur déploiement

BUT : Ce script prépare notre propre modèle fine-tuné spécialisé dans les addictions
ACTUELLEMENT : Nous utilisons l'API Hugging Face Inference
FUTUR :on va  remplacer l'API par ce modèle local pour plus de contrôle et de confidentialité
"""

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from peft import LoraConfig, get_peft_model
# =============================================================================
# PHASE 1: CONFIGURATION DU MODÈLE DE BASE
# =============================================================================

#  Charger modèle de base
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# =============================================================================
# PHASE 2: PRÉPARATION DES DONNÉES D'ENTRAÎNEMENT
# =============================================================================

# TODO: À AMÉLIORER 
# Futur: Remplacer par notre dataset complet d'addictions (tabac, alcool, cannabis)
# Source: data_loader.py + données médicales validées
# Charger jeu de données local
data = [
    {"prompt": "Comment arrêter de fumer ?", "response": "Réduisez petit à petit, demandez l’aide d’un professionnel."},
    {"prompt": "Quels sont les effets du cannabis ?", "response": "Altère la mémoire, la concentration et augmente l’anxiété."},
]
dataset = Dataset.from_list(data)

def preprocess(ex):
    inputs = tokenizer(ex["prompt"], truncation=True)
    labels = tokenizer(ex["response"], truncation=True)
    inputs["labels"] = labels["input_ids"]
    return inputs

dataset = dataset.map(preprocess, batched=False)

# =============================================================================
# PHASE 3: CONFIGURATION LoRA (Low-Rank Adaptation)
# =============================================================================

# TODO: À OPTIMISER - Hyperparamètres LoRA
# r=8: rang de la matrice d'adaptation (plus élevé = plus de capacité)
# lora_alpha: facteur d'échelle (32 valeur commune)
# target_modules: modules cibles dans le modèle (q, v pour T5)
# Appliquer LoRA
config = LoraConfig(r=8, lora_alpha=32, target_modules=["q", "v"], lora_dropout=0.1, bias="none")
model = get_peft_model(model, config)
# =============================================================================
# PHASE 4: CONFIGURATION DE L'ENTRAÎNEMENT
# =============================================================================

# TODO: À AJUSTER - Paramètres d'entraînement pour production
# Actuellement: entraînement rapide pour validation du concept
# Futur: Augmenter epochs, batch_size, et ajouter validation
# Entraînement rapide
args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    logging_steps=5
)

# =============================================================================
# PHASE 5: ENTRAÎNEMENT ET SAUVEGARDE
# =============================================================================
trainer = Trainer(model=model, args=args, train_dataset=dataset)
trainer.train()

# Sauvegarde
model.save_pretrained("chatbot-addicto-lora")
tokenizer.save_pretrained("chatbot-addicto-lora")
