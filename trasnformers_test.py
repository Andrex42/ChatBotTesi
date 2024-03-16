from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
from sentence_transformers.util import cos_sim


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Sentences we want sentence embeddings for
sentences = ["Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo, inoltre ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Ci sono state nuove tecniche innovative, ad esempio la prospettiva lineare e il chiaroscuro. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con più mobilità sociale e un cambiamento nei valori culturali.",
             "Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo. Questo periodo ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Gli artisti rinascimentali hanno introdotto tecniche innovative, come la prospettiva lineare e il chiaroscuro, portando a una nuova comprensione della rappresentazione visiva. L'educazione e l'alfabetizzazione divennero più diffuse, con un'élite culturale che si sviluppò nelle corti e nelle città, contribuendo alla nascita di una borghesia illuminata. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con una maggiore mobilità sociale e un cambiamento nei valori culturali, come l'individualismo e il primato dell'individuo rispetto alla comunità."]

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('nickprock/sentence-bert-base-italian-xxl-uncased')
model = AutoModel.from_pretrained('nickprock/sentence-bert-base-italian-xxl-uncased')


# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Perform pooling. In this case, mean pooling.
sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

print("Sentence embeddings:")
print(sentence_embeddings)

print("cosine_distances", cos_sim(sentence_embeddings[0], sentence_embeddings[1]))