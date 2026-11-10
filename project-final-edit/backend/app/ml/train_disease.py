import argparse, json
from pathlib import Path
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",required=True)
    parser.add_argument("--epochs",type=int,default=8)
    args=parser.parse_args()
    import tensorflow as tf
    data=Path(args.data_dir)
    train=tf.keras.utils.image_dataset_from_directory(data,validation_split=.2,subset="training",seed=42,image_size=(224,224),batch_size=32)
    valid=tf.keras.utils.image_dataset_from_directory(data,validation_split=.2,subset="validation",seed=42,image_size=(224,224),batch_size=32)
    names=train.class_names; autotune=tf.data.AUTOTUNE
    train=train.prefetch(autotune); valid=valid.prefetch(autotune)
    base=tf.keras.applications.MobileNetV2(input_shape=(224,224,3),include_top=False,weights="imagenet")
    base.trainable=False
    inputs=tf.keras.Input((224,224,3))
    x=tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x=base(x,training=False); x=tf.keras.layers.GlobalAveragePooling2D()(x)
    x=tf.keras.layers.Dropout(.25)(x); outputs=tf.keras.layers.Dense(len(names),activation="softmax")(x)
    model=tf.keras.Model(inputs,outputs)
    model.compile(optimizer="adam",loss="sparse_categorical_crossentropy",metrics=["accuracy"])
    model.fit(train,validation_data=valid,epochs=args.epochs)
    out=Path(__file__).resolve().parents[2]/"artifacts"; out.mkdir(parents=True,exist_ok=True)
    model.save(out/"disease_model.keras"); (out/"disease_classes.json").write_text(json.dumps(names,indent=2))
    print("Saved CNN model to",out)
if __name__=="__main__": main()
