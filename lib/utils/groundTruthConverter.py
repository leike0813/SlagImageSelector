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


def convert_groundTruth_single(
        segmentation, bbox, image_id, kernel, grayscale_incseq,
        region_prob_lb, normalized_grayscale_sampler, flags):
    boundary_mask = None
    boundary_mask_simple = None
    region_mask = None
    region_mask_simple = None

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
    boundary_mask = cv2.polylines(boundary_mask, [points_enlarged], True, 1)
    boundary_mask_simple = boundary_mask.copy()

    boundary_mask *= grayscale_incseq[0]
    for i in range(boundary_smooth_halfwidth - 1):
        _temp = cv2.dilate(boundary_mask_simple, kernel, iterations=i + 1)
        boundary_mask += _temp * grayscale_incseq[i + 1]

    if flags[2] or flags[3]:
        region_mask = np.zeros((bbox_enlarged[3] + 1, bbox_enlarged[2] + 1))
        region_mask = cv2.fillPoly(region_mask, [points_enlarged], 1)
        if flags[3]:
            region_mask_simple = region_mask.copy()

        if flags[2]:
            m = cv2.moments(points_enlarged)
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])

            boundary_points = []
            for _y in range(bbox_enlarged[3] + 1):
                for _x in range(bbox_enlarged[2] + 1):
                    if boundary_mask_simple[_y, _x]:
                        _rel_x = _x - int(cx)
                        _rel_y = _y - int(cy)
                        _rad = math.atan2(_rel_y, _rel_x)
                        _dist = math.sqrt(_rel_x ** 2 + _rel_y ** 2)
                        if _dist > 0:
                            boundary_points.append([_rad, _dist, _x, _y])

            boundary_points = np.array(boundary_points)
            _idx = np.argsort(boundary_points, axis=0)
            boundary_points = np.array([boundary_points[idx] for idx in _idx[:, 0]])
            rad_list = [-boundary_points[-1, 0]]
            dist_list = [boundary_points[-1, 1]]
            for i in range(boundary_points.shape[0]):
                rad_list.append(boundary_points[i, 0])
                dist_list.append(boundary_points[i, 1])

            dist_map_func = lambda x: np.interp(x, rad_list, dist_list)

            xc = np.linspace(0, bbox_enlarged[2], bbox_enlarged[2] + 1)
            yc = np.linspace(0, bbox_enlarged[3], bbox_enlarged[3] + 1)
            coord = np.meshgrid(xc, yc, indexing='xy')
            rel_coord = [coord[0] - cx, coord[1] - cy]
            rad_array = np.arctan2(rel_coord[1], rel_coord[0])
            dist_array = np.sqrt(rel_coord[0] ** 2 + rel_coord[1] ** 2)
            norm_dist_array = dist_array / dist_map_func(rad_array)

            prob_map_func = lambda x: normalized_grayscale_sampler(x, region_prob_lb)
            prob_map_ufunc = np.frompyfunc(prob_map_func, 1, 1)
            prob_cloud = prob_map_ufunc(norm_dist_array)
            prob_cloud = (prob_cloud / np.max(prob_cloud)).astype(np.float32)
            region_mask = region_mask * prob_cloud

    return boundary_mask, boundary_mask_simple, region_mask, region_mask_simple, bbox_enlarged, image_id


def insert_groundTruth_single(
        img, img_gt, category_name, category_color, gt_boundary_fld, gt_boundary_simple_fld,
        gt_region_fld, gt_region_simple_fld, validation_fld, flags):
    img_width = img['width']
    img_height = img['height']
    img_path = Path(img['path'])
    try:
        # img_orig = cv2.imread(img_path.as_posix())
        img_orig = cv2.imdecode(np.fromfile(img_path.as_posix()), cv2.IMREAD_COLOR)
    except Exception:
        img_orig = None

    img_boundary_mask = np.zeros((img_height, img_width))
    if flags[1]:
        img_boundary_simple_mask = np.zeros((img_height, img_width))
    if flags[2]:
        img_region_mask = np.zeros((img_height, img_width))
    if flags[3]:
        img_region_simple_mask = np.zeros((img_height, img_width))

    for gt in img_gt:
        img_boundary_mask = merge_mask(img_boundary_mask, gt[0], gt[-1])
        if flags[1]:
            img_boundary_simple_mask = merge_mask(img_boundary_simple_mask, gt[1], gt[-1])
        if flags[2]:
            img_region_mask = merge_mask(img_region_mask, gt[2], gt[-1])
        if flags[3]:
            img_region_simple_mask = merge_mask(img_region_simple_mask, gt[3], gt[-1])


    if np.max(img_boundary_mask) > 1:
        img_boundary_mask = np.clip(img_boundary_mask, 0, 1)
    if flags[1]:
        if np.max(img_boundary_simple_mask) > 1:
            img_boundary_simple_mask = np.clip(img_boundary_simple_mask, 0, 1)
    if flags[2]:
        if np.max(img_region_mask) > 1:
            img_region_mask = np.clip(img_region_mask, 0, 1)
    if flags[3]:
        if np.max(img_region_simple_mask) > 1:
            img_region_simple_mask = np.clip(img_region_simple_mask, 0, 1)
    if img_orig is not None:
        img_mask = np.stack([(img_boundary_mask * category_color[2]).astype(np.uint8),
                             (img_boundary_mask * category_color[1]).astype(np.uint8),
                             (img_boundary_mask * category_color[0]).astype(np.uint8)], axis=2)
        img_orig = cv2.addWeighted(img_orig, 1, img_mask, 0.5, 0)
        # cv2.imwrite((validation_fld / (img_path.stem + '_{cat}_validation.png'.format(cat=category_name))).as_posix(),
        #             img_orig)
        cv2.imencode('.png', img_orig)[1].tofile(
            (validation_fld / (img_path.stem + '_{cat}_validation.png'.format(cat=category_name))).as_posix())

    if flags[0]:
        # cv2.imwrite((gt_boundary_fld / (img_path.stem + '_{cat}_boundary.png'.format(cat=category_name))).as_posix(),
        #             (img_boundary_mask * 255).astype(np.uint8))
        cv2.imencode('.png', (img_boundary_mask * 255).astype(np.uint8))[1].tofile(
            (gt_boundary_fld / (img_path.stem + '_{cat}_boundary.png'.format(cat=category_name))).as_posix())
    if flags[1]:
        cv2.imencode('.png', (img_boundary_simple_mask * 255).astype(np.uint8))[1].tofile(
            (gt_boundary_simple_fld / (img_path.stem + '_{cat}_boundary_simple.png'.format(cat=category_name))).as_posix())
    if flags[2]:
        # cv2.imwrite((gt_region_fld / (img_path.stem + '_{cat}_region.png'.format(cat=category_name))).as_posix(),
        #             (img_region_mask * 255).astype(np.uint8))
        cv2.imencode('.png', (img_region_mask * 255).astype(np.uint8))[1].tofile(
            (gt_region_fld / (img_path.stem + '_{cat}_region.png'.format(cat=category_name))).as_posix())
    if flags[3]:
        cv2.imencode('.png', (img_region_simple_mask * 255).astype(np.uint8))[1].tofile(
            (gt_region_simple_fld / (img_path.stem + '_{cat}_region_simple.png'.format(cat=category_name))).as_posix())


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
    multiprocessConvertFlag = QtC.Signal(int)

    def __init__(self, parent=None):
        super(QGroundTruthConverter, self).__init__(parent)
        self.convert_groundTruth_single = convert_groundTruth_single
        self.insert_groundTruth_single = insert_groundTruth_single

    def convert(self, anno_path, category_name, boundary_smooth_halfwidth, boundary_smooth_coef, kernel_shape, region_prob_lb, flags):
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
        gt_boundary_simple_fld = img_root / 'GT_Boundary_Simple'
        gt_region_fld = img_root / 'GT_Region'
        gt_region_simple_fld = img_root / 'GT_Region_Simple'
        validation_fld = img_root / 'validation'
        if flags[0]:
            if not gt_boundary_fld.exists():
                os.makedirs(gt_boundary_fld)
        if flags[1]:
            if not gt_boundary_simple_fld.exists():
                os.makedirs(gt_boundary_simple_fld)
        if flags[2]:
            if not gt_region_fld.exists():
                os.makedirs(gt_region_fld)
        if flags[3]:
            if not gt_region_simple_fld.exists():
                os.makedirs(gt_region_simple_fld)
        if not validation_fld.exists():
            os.makedirs(validation_fld)

        anno_pd = pd.DataFrame(anno_json['annotations'])
        anno_infos = []
        for anno in anno_pd[anno_pd['category_id'] == category_id].iterrows():
            if len(anno[1]['segmentation'][0]) >= 6: # filter out invalid annotations
                anno_infos.append((
                    anno[1]['segmentation'],
                    anno[1]['bbox'],
                    anno[1]['image_id'],
                    kernel,
                    grayscale_incseq,
                    region_prob_lb,
                    self.normalized_grayscale_sampler,
                    flags
                ))

        self.converterMessage.emit('正在将图片标注转换为真值掩码...', self.MessageType.Information)
        self.multiprocessConvertFlag.emit(0)
        pool = mul.Pool(processes=os.cpu_count())
        gts = pool.starmap_async(
            self.convert_groundTruth_single,
            [anno_info for anno_info in anno_infos]).get()
        pool.close()
        pool.join()
        image_gts = {}
        for gt in gts:
            image_gt = image_gts.setdefault(gt[-1], [])
            image_gt.append(gt[:-1])
        self.multiprocessConvertFlag.emit(100)

        self.converterMessage.emit('正在合并真值掩码...', self.MessageType.Information)
        self.multiprocessConvertFlag.emit(0)
        img_infos = []
        for img in anno_json['images']:
            img_infos.append((
                img,
                image_gts[img['id']],
                category_name,
                category_color,
                gt_boundary_fld,
                gt_boundary_simple_fld,
                gt_region_fld,
                gt_region_simple_fld,
                validation_fld,
                flags
            ))
        pool = mul.Pool(processes=os.cpu_count())
        status = pool.starmap_async(
            self.insert_groundTruth_single,
            [img_info for img_info in img_infos]).get()
        pool.close()
        pool.join()
        self.multiprocessConvertFlag.emit(100)

        return True

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

    @staticmethod
    def normalized_grayscale_sampler(x, zero_map_prob=0.55):
        return (1 / math.sqrt(2 * math.pi)) * math.exp(
            -0.5 * math.sqrt(
                -2 * math.log(zero_map_prob)
            ) * math.sin(
                math.sin(x * math.pi / 2) * math.pi / 2
            ) ** 2
        )


if __name__ == '__main__':
    def convert(anno_path, category_name, boundary_smooth_halfwidth, boundary_smooth_coef, kernel_shape, region_prob_lb, flags):
        grayscale_seq = [QGroundTruthConverter.grayscale_sampler(x * boundary_smooth_coef) for x in range(boundary_smooth_halfwidth)]
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

        img_root = Path(anno_json['info']['image_root'])
        gt_boundary_fld = img_root / 'GT_Boundary'
        gt_boundary_simple_fld = img_root / 'GT_Boundary_Simple'
        gt_region_fld = img_root / 'GT_Region'
        gt_region_simple_fld = img_root / 'GT_Region_Simple'
        validation_fld = img_root / 'validation'
        if flags[0]:
            if not gt_boundary_fld.exists():
                os.makedirs(gt_boundary_fld)
        if flags[1]:
            if not gt_boundary_simple_fld.exists():
                os.makedirs(gt_boundary_simple_fld)
        if flags[2]:
            if not gt_region_fld.exists():
                os.makedirs(gt_region_fld)
        if flags[3]:
            if not gt_region_simple_fld.exists():
                os.makedirs(gt_region_simple_fld)
        if not validation_fld.exists():
            os.makedirs(validation_fld)

        anno_pd = pd.DataFrame(anno_json['annotations'])
        anno_infos = []
        for anno in anno_pd[anno_pd['category_id'] == category_id].iterrows():
            if len(anno[1]['segmentation'][0]) >= 6:
                anno_infos.append((
                    anno[1]['segmentation'],
                    anno[1]['bbox'],
                    anno[1]['image_id'],
                    kernel,
                    grayscale_incseq,
                    region_prob_lb,
                    QGroundTruthConverter.normalized_grayscale_sampler,
                    flags
                ))

        gts = []
        for anno_info in anno_infos:
            gts.append(convert_groundTruth_single(*anno_info))
            ii = 0

        image_gts = {}
        for gt in gts:
            image_gt = image_gts.setdefault(gt[-1], [])
            image_gt.append(gt[:-1])

        img_infos = []
        for img in anno_json['images']:
            img_infos.append((
                img,
                image_gts[img['id']],
                category_name,
                category_color,
                gt_boundary_fld,
                gt_boundary_simple_fld,
                gt_region_fld,
                gt_region_simple_fld,
                validation_fld,
                flags
            ))

        for img_info in img_infos:
            insert_groundTruth_single(*img_info)
            ii = 0


    anno_path = Path('/mnt/WinD/pythondata/datasets/slag_simple/label/annotations.json')
    kernel_shape = cv2.MORPH_ELLIPSE
    # region_masks, boundary_masks = converter.convert(anno_path, 'slag', 10, 0.3, kernel)
    convert(anno_path, 'slag', 10, 0.3, kernel_shape, 0.55, [True, True, True, True])

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

    ii = 0