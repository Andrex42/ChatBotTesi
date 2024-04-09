import pandas as pd
from sentence_transformers import InputExample, SentenceTransformer, models
from torch.utils.data import DataLoader
from sentence_transformers import evaluation
from sentence_transformers import losses


model_name = "nickprock/sentence-bert-base-italian-uncased"
enable_test = False

word_embedding_model = models.Transformer(model_name_or_path=model_name)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

df_risposte = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
df_risposte_docente = pd.read_csv('./training_data/risposte_docente_archeologia_storia_arte.csv')
df_risposte_test = pd.read_csv('training_data/risposte_test.csv')

risposte_dict = df_risposte.to_dict('records')
risposte_docente_dict = df_risposte_docente.to_dict('records')
risposte_test_dict = df_risposte_test.to_dict('records')

train_examples = []
test_dataset = []

for idx, item in enumerate(risposte_dict):
    domanda = item['title']
    risposta = item['text']
    punteggio = item['label']

    risposta_riferimento = None
    for ref_idx, ref_item in enumerate(risposte_docente_dict):
        if domanda == ref_item['title']:
            risposta_riferimento = ref_item['text']
            break

    if risposta_riferimento:
        train_examples.append(InputExample(texts=[risposta_riferimento, risposta],
                                           label=punteggio / 5.0))  # normalizziamo il punteggio nel range 0, 1
        # print(risposta_riferimento, "|", risposta, "|", punteggio / 5)


for idx, item in enumerate(risposte_test_dict):
    domanda = item['title']
    risposta = item['text']
    punteggio = item['label']

    risposta_riferimento = None
    for ref_idx, ref_item in enumerate(risposte_docente_dict):
        if domanda == ref_item['title']:
            risposta_riferimento = ref_item['text']
            break

    if risposta_riferimento:
        test_dataset.append([risposta_riferimento, risposta, punteggio])
        # print(risposta_riferimento, "|", risposta, "|", punteggio / 5)

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)

print(test_dataset)
evaluator = evaluation.EmbeddingSimilarityEvaluator(
    [t[0] for t in test_dataset], [t[1] for t in test_dataset], [t[2]/5.0 for t in test_dataset],
    main_similarity=evaluation.SimilarityFunction.COSINE,
    show_progress_bar=True,
    write_csv=True)

train_loss = losses.CosineSimilarityLoss(model=model)

# fit the model
num_epochs = 2
evaluation_steps = 10
steps_per_epoch = 30

warmup_steps = int(len(train_dataloader) * num_epochs * 0.05)  # 5% of train data
model.fit(train_objectives=[(train_dataloader, train_loss)],
          evaluator=evaluator,
          evaluation_steps=evaluation_steps,
          epochs=num_epochs,
          steps_per_epoch=steps_per_epoch,
          warmup_steps=warmup_steps,
          output_path="./fine_tuning",
          save_best_model=True)
