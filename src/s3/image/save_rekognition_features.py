def save_rekognition_features(self):

    table_path = self.rekognition_features_path
    for idx, row in tqdm(df.iterrows(), total=len(df)):
    if type(row['labels']) == list:
        continue 
    image = MyRekognitionImage(path=f'{global_image_folder}/{row["uuid"]}.png')
    row['text'] = [image.get_text()]
    row['labels'] = image.get_labels(max_labels=max_labels)
    row['faces'] = image.get_faces()
    if idx % 5 == 2:
        save_csv_to_s3(df=df, path=table_path, index=False)
save_csv_to_s3(df=df, path=table_path, index=False)