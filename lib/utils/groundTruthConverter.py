# -*- coding: utf-8 -*-
import os
import math
from enum import IntEnum
from pathlib import Path
import multiprocessing as mul
import json
import numpy as np
import pandas as pd
import cv2
import PySide2.QtCore as QtC


__all__ = ['QGroundTruthConverter']


def convert_groundTruth_single(segmentation, bbox, kernel, grayscale_incseq):
    points = np.array(segmentation).reshape(-1, 2).astype(int)
    bbox = [int(i) for i in bbox]
    boundary_smooth_halfwidth = len(grayscale_incseq)

    bbox_enlarged = [
        bbox[0] - boundary_smooth_halfwidth + 1,
        bbox[1] - boundary_smooth_halfwidth + 1,
        bbox[2] + 2 * boundary_smooth_halfwidth - 2,
        bbox[3] + 2 * boundary_smooth_halfwidth - 2
    ]
    points_enlarged = points.copy()
    points_enlarged[:, 0] = points[:, 0] - bbox_enlarged[0]
    points_enlarged[:, 1] = points[:, 1] - bbox_enlarged[1]
    boundary_mask = np.zeros((bbox_enlarged[3] + 1, bbox_enlarged[2] + 1))
    region_mask = np.zeros((bbox_enlarged[3] + 1, bbox_enlarged[2] + 1))

    boundary_mask = cv2.polylines(boundary_mask, [points_enlarged], True, 1)
    boundary_mask_simple = boundary_mask.copy()
    boundary_mask *= grayscale_incseq[0]
    for i in range(boundary_smooth_halfwidth - 1):
        _temp = cv2.dilate(boundary_mask_simple, kernel, iterations=i + 1)
        boundary_mask += _temp * grayscale_incseq[i + 1]

    region_mask = cv2.fillPoly(region_mask, [points_enlarged], 1)

    return region_mask, boundary_mask, bbox_enlarged


class QGroundTruthConverter(QtC.QObject):
    class MessageType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    class KernelShape(IntEnum):
        Ellipse = cv2.MORPH_ELLIPSE
        Rectangle = cv2.MORPH_RECT
        Cross = cv2.MORPH_CROSS

    converterMessage = QtC.Signal(str, int)
    convertGroundTruthMilestone = QtC.Signal(int)
    def __init__(self, parent=None):
        super(QGroundTruthConverter, self).__init__(parent)
        self.convert_groundTruth_single = convert_groundTruth_single

    def convert(self, anno_path, category_name, boundary_smooth_halfwidth, boundary_smooth_coef, kernel_shape):
        grayscale_seq = [self.grayscale_sampler(x * boundary_smooth_coef) for x in range(boundary_smooth_halfwidth)]
        grayscale_seq = [x / max(grayscale_seq) for x in grayscale_seq]
        grayscale_incseq = [grayscale_seq[i] - grayscale_seq[i + 1] for i in range(boundary_smooth_halfwidth - 1)]
        grayscale_incseq.append(grayscale_seq[boundary_smooth_halfwidth - 1])
        kernel = cv2.getStructuringElement(kernel_shape, (3, 3))

        with open(anno_path, 'r') as f:
            anno_json = json.load(f)

        _category_found = False
        for cat in anno_json['categories']:
            if cat['name'].lower() == category_name.lower():
                category_id = cat['id']
                category_color = cat['color']
                _category_found = True

        if not _category_found:
            self.converterMessage.emit('未能在标注文件中寻找到类别"{cat}"的信息'.format(cat=category_name),
                                       self.MessageType.Critical)
            return False

        img_root = Path(anno_json['info']['image_root'])
        gt_boundary_fld = img_root / 'GT_Boundary'
        gt_region_fld = img_root / 'GT_Region'
        validation_fld = img_root / 'validation'
        if not gt_boundary_fld.exists():
            os.makedirs(gt_boundary_fld)
        if not gt_region_fld.exists():
            os.makedirs(gt_region_fld)
        if not validation_fld.exists():
            os.makedirs(validation_fld)

        anno_pd = pd.DataFrame(anno_json['annotations'])
        totoal_images_to_convert = len(anno_json['images'])
        img_cnt = 0
        self.converterMessage.emit('正在将图片标注转换为真值掩码...', self.MessageType.Information)
        self.convertGroundTruthMilestone.emit(0)
        for img in anno_json['images']:
            img_id = img['id']
            img_width = img['width']
            img_height = img['height']
            img_path = Path(img['path'])
            try:
                img_orig = cv2.imread(img_path.as_posix())
            except Exception:
                img_orig = None
            img_boundary_mask = np.zeros((img_height, img_width))
            img_region_mask = np.zeros((img_height, img_width))
            anno_infos = []
            for anno in anno_pd[(anno_pd['image_id'] == img_id) & (anno_pd['category_id'] == category_id)].iterrows():
                anno_infos.append((anno[1]['segmentation'], anno[1]['bbox'], kernel, grayscale_incseq))

            pool = mul.Pool(processes=os.cpu_count())
            gts = pool.starmap_async(
                self.convert_groundTruth_single,
                [anno_info for anno_info in anno_infos]).get()
            pool.close()
            pool.join()

            for gt in gts:
                img_boundary_mask = self.merge_mask(img_boundary_mask, gt[1], gt[2])
                img_region_mask = self.merge_mask(img_region_mask, gt[0], gt[2])

            if np.max(img_boundary_mask) > 1:
                img_boundary_mask = np.clip(img_boundary_mask, 0, 1)
            if np.max(img_region_mask) > 1:
                img_region_mask = np.clip(img_region_mask, 0, 1)
            if img_orig is not None:
                img_mask = np.stack([(img_boundary_mask * category_color[2]).astype(np.uint8),
                                     (img_boundary_mask * category_color[1]).astype(np.uint8),
                                     (img_boundary_mask * category_color[0]).astype(np.uint8)], axis=2)
                img_orig = cv2.addWeighted(img_orig, 1, img_mask, 0.5, 0)
                cv2.imwrite((validation_fld / (img_path.stem + '_{cat}_validation.png'.format(cat=category_name))).as_posix(),
                            img_orig)

            cv2.imwrite((gt_boundary_fld / (img_path.stem + '_{cat}_boundary.png'.format(cat=category_name))).as_posix(),
                        (img_boundary_mask * 255).astype(np.uint8))
            cv2.imwrite((gt_region_fld / (img_path.stem + '_{cat}_region.png'.format(cat=category_name))).as_posix(),
                        (img_region_mask * 255).astype(np.uint8))

            img_cnt += 1
            self.convertGroundTruthMilestone.emit(math.floor(img_cnt / (totoal_images_to_convert / 100)))

        # return img_region_mask, img_boundary_mask # for debugging
        return True

    @staticmethod
    def merge_mask(orig_mask, new_mask, bbox):
        img_width = orig_mask.shape[1]
        img_height = orig_mask.shape[0]
        orig_area_width_lower = bbox[0] if bbox[0] >= 0 else 0
        orig_area_height_lower = bbox[1] if bbox[1] >= 0 else 0
        orig_area_width_upper = min(bbox[0] + bbox[2], img_width - 1)
        orig_area_height_upper = min(bbox[1] + bbox[3], img_height - 1)
        orig_area = orig_mask[
                    orig_area_height_lower: orig_area_height_upper + 1,
                    orig_area_width_lower: orig_area_width_upper + 1]
        new_area_width_lower = 0 if bbox[0] >= 0 else -bbox[0]
        new_area_height_lower = 0 if bbox[1] >= 0 else -bbox[1]
        new_area_width_upper = bbox[2] \
            if bbox[0] + bbox[2] <= img_width - 1 else img_width - 1 - bbox[0]
        new_area_height_upper = bbox[3] \
            if bbox[1] + bbox[3] <= img_height - 1 else img_height - 1 - bbox[1]
        new_area = new_mask[
                   new_area_height_lower: new_area_height_upper + 1,
                   new_area_width_lower: new_area_width_upper + 1]
        orig_area += new_area

        return orig_mask

    def annotationCompatibilityCheck(self, fld):
        if not isinstance(fld, Path):
            fld = Path(fld)
        if fld.is_file():
            annotation_path = fld
            fld = fld.parent.parent
        else:
            annotation_path = (fld / 'label') / 'annotations.json'
        if not annotation_path.exists():
            self.converterMessage.emit(
                '未发现标注文件',
                self.MessageType.Warning
            )
            return None
        try:
            with open(annotation_path, 'r') as _anno:
                annotations = json.load(_anno)
        except json.decoder.JSONDecodeError as e:
            self.converterMessage.emit(
                '无法读取"{ant}"'.format(ant=str(annotation_path)),
                self.MessageType.Warning
            )
            return None

        _imgRootMismatch = False
        _imgNameMismatch = False

        image_names = set([path.name for path in fld.glob('*.jpg')])
        total_images = len(image_names)
        try:
            annotation_image_root = annotations['info'].get('image_root', '')
            if annotation_image_root != fld.as_posix():
                _imgRootMismatch = True
            _imgCountMismatch = len(annotations['images']) - total_images # positive means more images in annotation
            for j in range(len(annotations['images'])):
                imgName = annotations['images'][j]['file_name']
                if imgName not in image_names:
                    _imgNameMismatch = True
                    break
        except KeyError:
            self.converterMessage.emit(
                '"{ant}"缺失关键键值'.format(ant=str(annotation_path)),
                self.MessageType.Warning
            )
            return None

        message = '当前标注文件所在文件夹存在以下问题:'
        if _imgRootMismatch:
            message += '\n- 标注文件的图片根目录与所在文件夹不一致, 可能由于文件移动或跨平台导致'
        if _imgCountMismatch != 0 or _imgNameMismatch:
            message += '\n- 文件夹中的原始图像与标注文件中的记录不符'
        message += '\n以上问题可能导致无法正确生成标注验证文件, 请确保标注信息的准确'

        if _imgCountMismatch != 0 or _imgNameMismatch or _imgRootMismatch:
            self.converterMessage.emit(
                message,
                self.MessageType.Warning
            )
        return annotations['categories']

    @staticmethod
    def grayscale_sampler(x):
        return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x ** 2)


if __name__ == '__main__':
    anno_path = Path('/mnt/WinD/pythondata/PyTorch/data/slag_simple/label/annotations.json')
    converter = QGroundTruthConverter()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # region_masks, boundary_masks = converter.convert(anno_path, 'slag', 10, 0.3, kernel)
    converter.convert(anno_path, 'slag', 10, 0.3, kernel)

    #
    # mask = boundary_masks
    # mask_image = np.stack([(mask * 59).astype(np.uint8),
    #                        (mask * 108).astype(np.uint8),
    #                        (mask * 244).astype(np.uint8)], axis=2)
    # # mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGRA2BGR)
    # img = cv2.imread(str(anno_path.parent.parent / '2023-06-03T17-27-25.554.jpg'))
    # img_weighted = cv2.addWeighted(img, 1, mask_image, 0.5, 0)
    # mask_copy = (mask * 255).astype(np.uint8)
    #
    #
    #
    # cv2.namedWindow('image')
    # cv2.imshow('image', img_weighted)
    # cv2.waitKey()
    # cv2.destroyAllWindows()