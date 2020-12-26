import os

import argparse

from utils.COCO_Utils.COCO_like_dataset import CocoLikeDataset 
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt



if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset_name', help='dataset name', type=str, choices=['DocExplore', 'flickrlogos_47'], default='DocExplore')
    parser.add_argument('-coco_images', help='image directory in coco format', type=str, default = '/mnt/BE6CA2E26CA294A5/Datasets/DocExplore_COCO/images')
    parser.add_argument('-annotation_json', help='image directory in coco format', type=str, default = '/mnt/BE6CA2E26CA294A5/Datasets/DocExplore_COCO/annotations/instances.json')
    parser.add_argument('-query_path', help='path to queries', type=str, default = '/mnt/BE6CA2E26CA294A5/Datasets/DocExplore_COCO/images/queries/')
    parser.add_argument('-model', help='model used for the convolutional features', type=str, choices=['resnet', 'VGG16'], default='VGG16') 
    parser.add_argument('-layer', help='resnet layer used for extraction', type=str, choices=['conv1_relu', 'conv2_block3_out', 'conv3_block4_out', 'conv4_block6_out', 'conv5_block3_out', 'block3_conv3', 'block4_conv3', 'block5_conv3'], default='block3_conv3') 
    parser.add_argument('-feat_savedir', help='directory of features database', type=str, default='/home/jeancherubini/Documents/feature_maps')

    params = parser.parse_args()    


    #creation of dataset like coco
    train_images = CocoLikeDataset()
    train_images.load_data(params.annotation_json, params.coco_images)
    train_images.prepare()

    #Open all detections document
    all_detections_ordered = open('{0}/{1}/{2}/detections/all_detections_ordered.txt'.format(params.feat_savedir, params.dataset_name, params.model + '_' + params.layer),'r')

    #Create dict to group by query for pattern spotting
    detections_by_query_id = {}
    recoveries_by_query_id = {}
    counter_query_id = {}
    for row in all_detections_ordered:
        #image retrieval
        query_id, image_detected, x1, y1, width, height, value, query_class = row.split(' ') 
        
        image_info = train_images.image_info[int(image_detected)]
        page = os.path.basename(image_info['path'])
        page_cut_extension = page.replace('page','').replace('.jpg', '').replace('.png', '')
        #print(image_detected, page)

        x2 = int(x1)+int(width)
        y2 = int(y1)+int(height)
        
        try:
            if counter_query_id[query_id]<1000:
                detections_by_query_id[query_id]+= ('{0}-{1}-{2}-{3}-{4} '.format(page_cut_extension, x1, y1, x2, y2))
                recoveries_by_query_id[query_id]+= ('{0}\t'.format(page_cut_extension))

                counter_query_id[query_id] += 1

        except:
            detections_by_query_id[query_id] = '{0}-{1}-{2}-{3}-{4} '.format(page_cut_extension, x1, y1, x2, y2)
            recoveries_by_query_id[query_id] = ('{0}\t'.format(page_cut_extension))

            counter_query_id[query_id] = 1

                


    #open file to sav ps
    ps_for_DocExplore = open('{0}/{1}/{2}/detections/ps_for_DocExplore.txt'.format(params.feat_savedir, params.dataset_name, params.model + '_' + params.layer),'w')
    ir_for_DocExplore = open('{0}/{1}/{2}/detections/ir_for_DocExplore.txt'.format(params.feat_savedir, params.dataset_name, params.model + '_' + params.layer),'w')


    for query_class in os.listdir(params.query_path):
        for query_instance in os.listdir(params.query_path + '/' + query_class):
            try:
                ps_for_DocExplore.write('{0}:{1}\n'.format(query_instance.replace('.jpg', '').replace('.png',''), detections_by_query_id[query_instance.replace('.jpg', '').replace('.png','')]))
                ir_for_DocExplore.write('{0}:{1}\n'.format(query_instance.replace('.jpg', '').replace('.png',''), recoveries_by_query_id[query_instance.replace('.jpg', '').replace('.png','')]))

            except:
                ps_for_DocExplore.write('{0}:0-0-0-0-0\n'.format(query_instance.replace('.jpg', '').replace('.png','')))
                ir_for_DocExplore.write('{0}:\n'.format(query_instance.replace('.jpg', '').replace('.png','')))


    '''
    for query in detections_by_query_id.keys():
        ps_for_DocExplore.write('{0}:{1}\n'.format(query, detections_by_query_id[query]))
    '''
    ps_for_DocExplore.close()
    ir_for_DocExplore.close()