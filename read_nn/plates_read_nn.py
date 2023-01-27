import numpy as np
import tensorflow as tf
from generate.plates_generate import create_plates
from utils import load_images_dict_from_folder
import cv2
from unet_model import IMG_SIZE, build_unet_model
from sklearn.model_selection import train_test_split


# this will be needed for pretty pic of the model for presentation/report
def plot_model(model):
    tf.keras.utils.plot_model(model, to_file="unet_model.png", show_shapes=True, show_dtype=False,
                              show_layer_names=True, rankdir="TB", expand_nested=False,
                              dpi=96, layer_range=None, show_layer_activations=True, )


def create_mask(pred_mask):
    pred_mask = tf.argmax(pred_mask, axis=-1)
    pred_mask = pred_mask[..., tf.newaxis]
    return pred_mask[0]


def show_predictions(X_val, Y_val, num=1):
    # result of predictions has shape (256, 256, 3) and contains values from 0 to 1
    pred_masks = model.predict(X_val)
    for i, image in enumerate(X_val):
        mask = Y_val[i]
        # concatenate image Horizontally
        pred_mask = pred_masks[i]

        # eye test
        cv2.imshow("Original", np.uint8(image))
        cv2.imshow("Original Mask", np.uint8(mask))
        cv2.imshow("Predicted Mask", np.uint8(pred_mask * 255))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if i > 5:
            break


# If the plates and masks folders are empty or don't contain enough elements, clear them and run this line
# create_plates(10000)

# Load and preprocess the images and masks
plates_dict = load_images_dict_from_folder("database/plates")
plates = list(plates_dict.values())
plates = np.reshape(plates, (len(plates), IMG_SIZE, IMG_SIZE, 3))

# plates = [tf.image.resize(plate, (IMG_SIZE, IMG_SIZE), method="nearest") for plate in plates] - no need, since images are generated 256*256 now

masks_dict = load_images_dict_from_folder("database/masks")
masks = list(masks_dict.values())
masks = np.reshape(masks, (len(masks), IMG_SIZE, IMG_SIZE, 3))
# masks = [tf.image.resize(mask, (IMG_SIZE, IMG_SIZE), method="nearest") for mask in masks] - no need, since images are generated 256*256

# To check the mask and plate eye test:
# cv2.imshow("Plate", np.uint8(plates[0]))
# cv2.imshow("Mask", np.uint8(masks[0]))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Create dataset and split it into train, validation and test + split into batches
X_train, X_val, Y_train, Y_val = train_test_split(plates, masks, random_state=104, test_size=0.3, shuffle=True)

# Build the U-Net model
model = build_unet_model(IMG_SIZE)
model.summary()
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

NUM_EPOCHS = 100
BATCH_SIZE = 64
model.fit(X_train, Y_train, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, validation_data=(X_val, Y_val), verbose=1)

model.save("read_nn/unet")
print("model saved: read_nn/unet")

# After you created and trained the model, it will get saved in read_nn/unet, so you can just load it from there instead of re-training it every time:
# model = tf.keras.models.load_model('read_nn/unet')

show_predictions(X_val, Y_val)