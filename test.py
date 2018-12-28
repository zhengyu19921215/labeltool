import os,sys
import keras.backend as K
import numpy as np
from PIL import Image

sys.path.append(os.getcwd()+'/text-detection-ctpn-master')
print(os.getcwd()+'/text-detection-ctpn-master')

from lib.fast_rcnn.config import cfg, cfg_from_file
from lib.fast_rcnn.test import _get_blobs
from lib.text_connector.detectors import TextDetector
from lib.text_connector.text_connect_cfg import Config as TextLineCfg
from lib.rpn_msr.proposal_layer_tf import proposal_layer
import cv2
from CRNN_Keras.parameter import letters, img_h
import datetime



# from keras.models import load_model



    # model.load_weights(modelPath)


def predict(save_file,keras_model):
    """
    输入图片，输出keras模型的识别结果
    """
    img = cv2.imread(save_file, cv2.IMREAD_GRAYSCALE)

    scale = img.shape[0] * 1.0 / img_h
    w = img.shape[1] / scale
    w = int(w)
    img = cv2.resize(img, (w, img_h))
    img_pred = img.astype(np.float32)
    img_pred = (img_pred / 255.0) * 2.0 - 1.0
    # img_pred = img_pred.T
    img_pred = np.expand_dims(img_pred, axis=-1)
    img_pred = np.expand_dims(img_pred, axis=0)

    net_out_value = keras_model.predict(img_pred)
    y_pred = net_out_value[:, 2:, :]
    # pred_texts = decode_label(net_out_value)

    out = K.get_value(K.ctc_decode(y_pred, input_length=np.ones(y_pred.shape[0]) * y_pred.shape[1], )[0][0])[:, :]
    char_list = ''
    n = len(letters)
    t = out[0]
    for i in range(len(t)):
        if letters[t[i]]==' ':
            continue
        char_list = char_list + letters[t[i]]

    return char_list




def resize_im(im, scale, max_scale=None):
    f = float(scale) / min(im.shape[0], im.shape[1])
    if max_scale != None and f * max(im.shape[0], im.shape[1]) > max_scale:
        f = float(max_scale) / max(im.shape[0], im.shape[1])
    return cv2.resize(im, None, None, fx=f, fy=f, interpolation=cv2.INTER_LINEAR), f

def draw_boxes(img, image_name, boxes, scale,keras_model):
    base_name = image_name.split('/')[-1]
    im0 = Image.open(image_name)
    #im0=cv2.imread(image_name,cv2.IMREAD_GRAYSCALE)
    #predition_result={}
    #predition_result['box']=[]
    #predition_result['result'] = []
    #predition_result['file'] = []
    j=0
    #with open('upload/result/' + 'res_{}.txt'.format(base_name.split('.')[0]), 'w') as f:
    for box in boxes:
        if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3] - box[0]) < 5:
            continue
        if box[8] >= 0.9:
            color = (0, 255, 0)
        elif box[8] >= 0.8:
            color = (255, 0, 0)
        cv2.line(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, 2)
        cv2.line(img, (int(box[0]), int(box[1])), (int(box[4]), int(box[5])), color, 2)
        cv2.line(img, (int(box[6]), int(box[7])), (int(box[2]), int(box[3])), color, 2)
        cv2.line(img, (int(box[4]), int(box[5])), (int(box[6]), int(box[7])), color, 2)

        min_x = min(int(box[0] / scale), int(box[2] / scale), int(box[4] / scale), int(box[6] / scale))
        min_y = min(int(box[1] / scale), int(box[3] / scale), int(box[5] / scale), int(box[7] / scale))
        max_x = max(int(box[0] / scale), int(box[2] / scale), int(box[4] / scale), int(box[6] / scale))
        max_y = max(int(box[1] / scale), int(box[3] / scale), int(box[5] / scale), int(box[7] / scale))
        '''
        if max_x-min_x>=800:
            img_box=(min_x,min_y,max_x-640,max_y)
            mini_img = im0.crop(img_box)
            save_file = 'upload/result/' + base_name.split('.')[0] + '_' + str(j) + '_0.png'
            mini_img.save(save_file)
            sim_pred = predict(save_file, keras_model)
            predition_result['box'].append(img_box)
            predition_result['result'].append(sim_pred)
            predition_result['file'].append(save_file)
            with open('upload/result/predict.txt', 'a') as f1:
                f1.write(save_file + '\n' + sim_pred + '\n')
            img_box = (max_x-640, min_y, max_x , max_y)
            mini_img = im0.crop(img_box)
            save_file = 'upload/result/' + base_name.split('.')[0] + '_' + str(j) + '_1.png'
            mini_img.save(save_file)
            sim_pred = predict(save_file, keras_model)
            predition_result['box'].append(img_box)
            predition_result['result'].append(sim_pred)
            predition_result['file'].append(save_file)
            with open('upload/result/predict.txt', 'a') as f1:
                f1.write(save_file + '\n' + sim_pred + '\n')
            f1.close()
            line = ','.join([str(min_x), str(min_y), str(max_x), str(max_y)]) + '\r\n'
            f.write(line)
            continue
        '''

        img_box = (min_x,min_y,max_x,max_y)
        save_file='auto_detect_recognition/split_result/' + base_name.split('.')[0] + '_' + str(j) + '.png'
        mini_img = im0.crop(img_box)
        mini_img.save(save_file)
        starttime = datetime.datetime.now()

        sim_pred = predict(save_file,keras_model)
        endtime = datetime.datetime.now()
        print(endtime - starttime)
        #predition_result['box'].append(img_box)
        #predition_result['result'].append(sim_pred)
        #predition_result['file'].append(save_file)
        with open('auto_detect_recognition/label.txt', 'a') as f1:
            f1.write(base_name.split('.')[0] + '_' + str(j) + '.png'+'\n'+sim_pred + '\n')
        f1.close()
        j=j+1

            #line = ','.join([str(min_x), str(min_y), str(max_x), str(max_y)]) + '\r\n'
            #f.write(line)


    #img = cv2.resize(img, None, None, fx=1.0 / scale, fy=1.0 / scale, interpolation=cv2.INTER_LINEAR)
    #cv2.imwrite(os.path.join("upload/crop_img/", base_name), img)
    #return predition_result




def test(im_name,sess,output_cls_prob,output_box_pred,input_img,keras_model):
   # im_name='test.jpg'###测试图片名字
    starttime = datetime.datetime.now()
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(('Demo for {:s}'.format(im_name)))
    img = cv2.imread(im_name)
    img, scale = resize_im(img, scale=TextLineCfg.SCALE, max_scale=TextLineCfg.MAX_SCALE)
    blobs, im_scales = _get_blobs(img, None)
    if cfg.TEST.HAS_RPN:
        im_blob = blobs['data']
        blobs['im_info'] = np.array(
            [[im_blob.shape[1], im_blob.shape[2], im_scales[0]]],
            dtype=np.float32)
    cls_prob, box_pred = sess.run([output_cls_prob, output_box_pred], feed_dict={input_img: blobs['data']})
    rois, _ = proposal_layer(cls_prob, box_pred, blobs['im_info'], 'TEST', anchor_scales=cfg.ANCHOR_SCALES)

    scores = rois[:, 0]
    boxes = rois[:, 1:5] / im_scales[0]
    textdetector = TextDetector()
    boxes = textdetector.detect(boxes, scores[:, np.newaxis], img.shape[:2])


    endtime = datetime.datetime.now()
    print('1')
    print(endtime - starttime)


    starttime = datetime.datetime.now()
    predition_result=draw_boxes(img, im_name, boxes, scale,keras_model)



    return predition_result

