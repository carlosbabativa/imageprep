import os
import re
import glob
import json
import numpy as np
from PIL import Image


def image_names(path_to_folder, with_extension=True):
    """
     Reads raster files from multiple folders and returns their names

    :param path_to_folder: directory path
    :param with_extension: file extension
    :return: names of the raster files
    """

    name_list = []

    # common image file extensions
    extension = ['jpg', 'png', 'tif', 'jpeg', 'tiff']

    if os.path.isdir(path_to_folder):
        files = os.listdir(path_to_folder)
        for f in files:
            if f.split('.')[-1] in extension:

                if with_extension is True:
                    name_list.append(f)
                else:
                    title, ext = f.split('.')
                    name_list.append(title)
    else:
        file = path_to_folder

        if file.split('.')[-1] in extension:

            if with_extension is True:
                name_list.append(file)
            else:
                title, ext = file.split('.')
                name_list.append(title)

    return name_list


def pad_image(image_file_name, new_size=(600, 600), save=False):

    """
     Pad Image with a given number of rows and columns

    :param image_file_name: image file
    :param new_size: now image size
    :return:
    """
    # src: https://stackoverflow.com/questions/11142851/adding-borders-to-an-image-using-python/39321668#39321668
    image = Image.open(image_file_name)
    rows, cols = image.size

    # Set number of pixels to expand to the left, top, right,
    # and bottom, making sure to account for even or odd numbers

    if rows % 2 == 0:
        add_left = add_right = (new_size[0] - rows) // 2
    else:
        add_left = (new_size[0] - rows) // 2
        add_right = ((new_size[0] - rows) // 2) + 1

    if cols % 2 == 0:
        add_top = add_bottom = (new_size[1] - cols) // 2
    else:
        add_top = (new_size[1] - cols[1]) // 2
        add_bottom = ((new_size[1] - cols[1]) // 2) + 1

    left = 0 - add_left
    top = 0 - add_top
    right = rows + add_right
    bottom = cols + add_bottom

    image = image.crop((left, top, right, bottom))

    if save is True:

        image.save('padded_output.png')

    return image


def resize_images_in_one_folder(path, output_size=256):
    """
     Re-sizes images in one folder

    :param path: path to the folder
    :param output_size: size of the image output
    :return: re-sized images saved in the same folder
    """
    dirs = os.listdir(path)
    for item in dirs:
        print(dirs)
        if os.path.isfile(path+item):
            if item.endswith(".jpg"):
                im = Image.open(path+item)
                f, e = os.path.splitext(path+item)

                imResize = im.resize((output_size,output_size), Image.ANTIALIAS)
                imResize.save(f + '.jpg', 'JPEG', quality=90)


def resize_images_from_multiple_folders(path, output_size=256):
    """
     Re-sizes images in multiple folders and saves images in each respective folder

    :param path: path to the folder containing all folders with images
    :return: re-sized images saved in their respective folder
    """

    for folders in os.listdir(path):
        folder_list = os.path.join(path,folders)
        for item in os.listdir(folder_list):
            if item.endswith(".png"):
                file = os.path.join(folder_list,item)

                im = Image.open(file)
                imResize = im.resize((output_size, output_size), Image.ANTIALIAS)

                f, e = os.path.splitext(file)
                imResize.save(f + '.png', 'JPEG', quality=90)


def yolo_label_format(size, box):
    """
     Rule to convert anchors to YOLO label format

    :param size: Height and width of the image as a list
    :param box: the four corners of the bounding box as a list
    :return: YOLO style labels
    """
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh

    return x, y, w, h


def reverse_yolo_to_anchor(size, box):
    """
     Reverse YOLO label format to anchors bbox

    :param size: Size of the image
    :param box: YOLO labels
    :return: Anchor bbox values
    """
    dw = size[0]
    dh = size[1]
    xmin = int(((dw * box[0]) * 2) - dw)
    ymin = int(((dh * box[1]) * 2) - dh)
    xmax = int((dw * box[2]) + xmin)
    ymax = int((dw * box[3]) + ymin)

    return xmin, ymin, xmax, ymax


def convert_to_yolo(input_label_path, image, output_label_path):
    """
     Converts labels to YOLO data format

    :param input_label_path: path to the folder containing the label files
    :param image: path to the corresponding images
    :param output_label_path: path to output folder for the YOLO labels
    :return: YOLO formatted label files
    """
    g = open("output.txt", "w")
    for file in os.listdir(input_label_path):

        if ".txt" in file:
            filename = file[:-4] + ".jpg"
            input_file = open(os.path.join(input_label_path + file))
            file = file[:-4] + '.txt'
            output_file = open(output_label_path + file, "w")
            file_path = image + filename

            g.write(file_path + "\n")
            for line in input_file.readlines():
                match = re.findall(r"(\d+)", line)

                if match:
                    xmin = float(match[0])
                    ymin = float(match[1])
                    xmax = float(match[2])
                    ymax = float(match[3])

                    b = (xmin, xmax, ymin, ymax)
                    im = Image.open(file_path)
                    size = im.size
                    bb = yolo_label_format(size, b)

                    output_file.write("0" + " " + " ".join([str(a) for a in bb]) + "\n")

            output_file.close()
            input_file.close()
    g.close()


def list_path_to_files(path_to_folders, output_file_name, output_file_extension='.png'):
    """
     Saves the path to files (images or labels) in one text file

    :param path_to_folders: path to the folder containing images or labels
    :param output_file_name: name of output text file
    :param output_file_extension: name of file extension for the output
    :return: a text file with a list of path to files
    """
    # common file extensions
    extension = ['jpg', 'png', 'tif', 'jpeg', 'tiff']

    txt = open(os.path.join(path_to_folders, output_file_name), 'w')
    counter = 0
    files = os.listdir(path_to_folders)

    for f in files:
        if f.split('.')[-1] in extension:
            title, ext = f.split('.')
            txt.write(path_to_folders + title + output_file_extension + "\n")
            counter = counter + 1


def read_image(file, as_array = True):
    """
     Reads image and returns a numpy array

    :param file: image file name
    :param as_array: option to read image to array.
    :return: numpy array
    """
    img = Image.open(file)
    if as_array is True:
        img = np.asarray(img)
    return img


def images_as_array(path, ext='.jpg'):
    """
     Reads multiple images in a folder and returns a stacked numpy array

    :param path: path to the folder containing the images
    :param ext: file extension. defaulted to jpg
    :return: stacked numpy array of images
    """

    dir = os.listdir(path)
    img_arr_list = []
    for item in dir:
        if os.path.isfile(path + item):
            if item.endswith(ext):
                img_arr = read_image(path+item)
                img_arr = np.expand_dims(img_arr, axis=0)
                img_arr_list.append(img_arr)

    img_stack = np.vstack(img_arr_list)

    return img_stack


def read_labels(input_path, ext='.txt'):
    """
     Read multiple label text files

    :param input_path: path to the folder containing the labels text files
    :param ext: name of file extension. defaulted to jpg
    :return:
    """

    folder = os.listdir(input_path)
    label_content = []
    for item in folder:
        if os.path.isfile(input_path+item):
            if item.endswith(ext):
                content = []
                input_file = open(os.path.join(input_path + item))
                for line in input_file.read().splitlines():
                    content.append([line])
                if len(content) !=1:
                    label_content.append([item, content])
                else:
                    label_content.append([item,content[0]])

    return label_content


def read_label_as_dict(file, ext='.txt'):
    """
     Reads a label file in text format as a dictionary

    :param file: Name of the label file
    :param ext: Name of the file extension. Defaulted to text
    :return: A dictionary of the label
    """
    label_content = {}
    if os.path.isfile(file):
        if file.endswith(ext):
            content = []
            input_file = open(file)
            for line in input_file.read().splitlines():
                content.append([line])
            if len(content) != 1:
                label_content['name'] = file
                label_content['bbox'] = content
            else:
                label_content['name'] = file
                label_content['bbox'] = content[0]

    return label_content


def read_label_as_list(file, ext='.txt'):
    """
     Reads a label file in text format as a list

    :param file: Name of the label file
    :param ext: Name of the file extension. Defaulted to text
    :return: Label as a list
    """
    label_content = []
    if os.path.isfile(file):
        if file.endswith(ext):
            content = []
            input_file = open(file)

            for line in input_file.read().splitlines():
                content.append([line])
            if len(content) != 1:
                label_content.append([file, content])
            else:
                label_content.append([file, content[0]])

    return label_content


def image_metadata(image, save=False):
    """
     Create a meta data JSON object for an image

    :param image: Path and name of the image
    :param save: Option to Save metadata to a JSON file
    :return: JSON object
    """
    obj = {}
    f_name = []
    img = Image.open(image)
    name = img.filename
    height, width = img.size

    f_name.append(name)
    obj['file_name'] = f_name[0]
    obj['height'] = height
    obj['width'] = width

    if save is True:
        output_file = 'data.json'

        with open(output_file, 'w') as f:
            json.dump(obj, f)

    return obj


def image_folder_metadata(path, save=False):
    """
     Creates a JSON metadata list for images in a folder

    :param path: Path to the folder containing the images
    :param save: Option to Save metadata to a JSON file
    :return: The list or JSON object of metadata
    """
    obj = {}
    extension = ['jpg', 'png', 'tif', 'jpeg', 'tiff']
    img_list = []

    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            if f.split('.')[-1] in extension:
                json_file = image_metadata(path+f)
                img_list.append(json_file)

    if save is True:
        obj['images'] = img_list
        output_file = 'data.json'
        with open(output_file, 'w') as f:
            json.dump(obj, f)

    return img_list


def image_folder_metadata_with_id(path,save=False):
    """
     Creates a JSON metadata with ID for images in a folder

    :param path: Path to the folder containing the images
    :param save: Option to Save metadata to a JSON file
    :return: The list or JSON object of metadata
    """
    obj = {}
    img_list = image_folder_metadata(path)


    obj['images'] = img_list

    for idx, v in enumerate(img_list):
        v['id'] = idx


    if save is True:
        output_file = 'data.json'
        with open(output_file, 'w') as f:
            json.dump(obj, f)

    return img_list


def bbox_reader(path):
    """
    {
      "id": 1,
      "bbox": [
        100,
        116,
        140,
        170
      ],
      "image_id": 0,
      "segmentation": [],
      "ignore": 0,
      "area": 23800,
      "iscrowd": 0,
      "category_id": 0
    }

    :param path:
    :return:
    """
    key_list = 'bbox'

    label_list = read_label_as_list(path)
    bbox = label_list[0][1]


    return bbox


def bbox_list(path):

    bb_dict = []
    key_list = ['bbox']
    bb_list = bbox_reader(path)

    for idx, bb in enumerate(bb_list):
        idx += 1
        if idx is not 1:
            bb_dz = dict(zip(key_list, [[bb[0].strip()]]))
            bb_dict.append(bb_dz)
        else:
            bb_dz = dict(zip(key_list, [bb]))

        bb_dict.append(bb_dz)

    return bb_dict


def bbox_coco(path):
    obj = {}
    bb_dict = bbox_list(path)
    # file_name = path.split('/')[-1].split('.')[0]
    obj['images'] = bb_dict

    for idx, value in enumerate(bb_dict):
        idx +=1
        value['id'] = idx

        bb_list = value['bbox'][0].split(' ')
        #print((bb_list))
        #xmin = int(bb_list[1].strip())
       # ymin = float(bb_list[1])
        #xmax = float(bb_list[2])
        #ymax = float(bb_list[3])
        #print(xmin, ymin)
        #w = xmax - xmin
        #h = ymax - ymin

        value["image_id"] = 0
        value["segmentation"] = []
        value["ignore"] = 0
        #value["area"] = h*w
        value["iscrowd"] = 0
        value["category_id"] = 0

    return bb_dict

