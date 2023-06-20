# -*- coding: utf-8 -*-
import os
import sys
import math
from datetime import datetime
from enum import IntEnum, IntFlag
from pathlib import Path
import multiprocessing as mul
import PIL.Image as PILImg
import json
import numpy as np
import cv2
import PySide2.QtCore as QtC
from lib.parameterizedImantics.utils import replace_absolute_image_path
from lib.parameterizedImantics import Annotation, Image, Category, Dataset, Color, Default_Config


__all__ = ['QAnnotationConverter', 'Default_Config']


_default_config = Default_Config.clone()


def convert_annotation_single(img_idx, img_path, category, config=_default_config, img_object=None):
    if not img_object:
        img_array = cv2.imread(img_path.as_posix())
        img = Image(img_array, id=img_idx, config=config)
        img.height = img_array.shape[0]
        img.width = img_array.shape[1]
        img.file_name = img_path.name
        img.path = img_path.as_posix()
    else:
        # img_object must be parameterizedImantics.Image object!
        # Skip type checking for multiprocessing, so make sure this interface will not be exposed to user.
        # When use img_object as input, parameter img_idx is irrelevant,
        #   but img_path is still essential for locate corresponding primitive mask file,
        #   and it will be better to match img_object.path property (however it is not necessary),
        #   the path checking is ignored for cross-platform compatibility.
        img = img_object

    img_prim_mask = np.array(PILImg.open((img_path.parent / 'result') / (img_path.stem + '.border.tif')), dtype=np.uint16)
    num_annotations = np.max(img_prim_mask)
    for i in range(1, num_annotations + 1):
        boundary_cv = ((img_prim_mask == i).astype(np.uint8) * 255).reshape((img.height, img.width, 1))
        region_mask = np.zeros((img.height + 2, img.width + 2), np.uint8)
        cv2.floodFill(boundary_cv, mask=region_mask, seedPoint=(0, 0), newVal=255)
        region_mask = 1 - region_mask
        polygons = cv2.findContours(region_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS, offset=(-1, -1))
        polygons = polygons[0] if len(polygons) == 2 else polygons[1]
        polygons = [polygon.flatten() for polygon in polygons]
        polygons = Annotation(image=img, category=category, polygons=polygons, config=config)
        img.add(polygons)
    return img


class QAnnotationConverter(QtC.QObject):
    """

    """
    class ConvertMode(IntEnum):
        New = 1
        Merge = 2
        Overwrite = 4

    class ConvertModeFlag(IntFlag):
        Reject = -1
        NoFlag = 0
        New = 1
        Merge = 2
        Overwrite = 4
        NeedRepair = 8
        Extractable = 16

    class MessageType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    converterMessage = QtC.Signal(str, int)
    buildAnnotationMilestone = QtC.Signal(int)
    multiprocessConvertFlag = QtC.Signal(int)

    def __init__(self, config=_default_config, parent=None):
        super(QAnnotationConverter, self).__init__(parent)
        self.dataset = None
        self.category = None
        self.config = config
        self.convert_annotation_single = convert_annotation_single

    def build_dataset(self, fld, mode, category_name, category_color, category_id=1, dataset_name='Default'):
        """
        Generates a dataset from a custom folder with original images and primitive boundary masks
        :param fld: valid pathlib.Path object or path string
        :param mode: convert mode, can be cls.ConvertMode.{New | Merge | Overwrite} or integer {1 | 2 | 3}
        :param category_name: name of category
        :param category_color: color of category (R, G, B)
        :param category_id: id of category, default: 1
        :param dataset_name: name of dataset
        :return: Dataset object
        """
        if not (fld / 'result').exists():
            self.converterMessage.emit(
                '用于存放原始边界掩码的子文件夹"result"不存在', self.MessageType.Critical)
            return None
        self.workFld = fld
        # self.config.IMAGE.IMAGE_ROOT = str(self.workFld)
        annotation_path = (self.workFld / 'label') / 'annotations.json'
        if mode == self.ConvertMode.Merge:
            if annotation_path.exists():
                try:
                    with open(annotation_path, 'r') as f_coco:
                        coco_obj = json.load(f_coco)

                    self.dataset = Dataset.from_coco(coco_obj, name=dataset_name, config=self.config)
                    category_found = False
                    max_category_id = 1
                    for cat in self.dataset.iter_categories():
                        if cat.name.lower() == category_name.lower():
                            category_found = True
                            self.category = cat
                            break
                        max_category_id = max(max_category_id, cat.id)
                    if not category_found:
                        self.category = Category(
                            category_name, id=max_category_id,
                            color=Color(rgb=category_color, config=self.config),
                            config=self.config
                        )
                    self.dataset._mergedImages = set()
                    for img in self.dataset.iter_images():
                        self.dataset._mergedImages.add(img.path)
                    self.dataset._merged = annotation_path
                    self.mode = mode

                except json.decoder.JSONDecodeError as e:
                    self.converterMessage.emit(
                        '无法读取"{ant}", 采用覆写模式'.format(ant=str(annotation_path)),
                        self.MessageType.Warning
                    )

                    self.mode = self.ConvertMode.Overwrite
            else:
                self.mode = self.ConvertMode.New
        else:
            self.mode = mode

        if self.mode == self.ConvertMode.New or self.mode == self.ConvertMode.Overwrite:
            self.dataset = Dataset(dataset_name, image_root=self.workFld.as_posix(), config=self.config)
            self.category = Category(
                category_name, id=category_id,
                color=Color(rgb=category_color, config=self.config)
                , config=self.config
            )

        return self.dataset

    def convert_annotations(self):
        image_paths = [path for path in self.workFld.glob('*.jpg')]
        total_images = len(image_paths)
        cur_img_idx = len(self.dataset.images) + 1
        image_to_convert = []
        for img_idx, img_path in enumerate(image_paths):
            if self.mode == self.ConvertMode.Merge and img_path.as_posix() in self.dataset._mergedImages:
                continue
            elif not ((self.workFld / 'result') / (img_path.stem + '.border.tif')).exists():
                continue
            else:
                image_to_convert.append((cur_img_idx, img_path, self.category, self.config))
                cur_img_idx += 1
        totoal_images_to_convert = len(image_to_convert)
        if totoal_images_to_convert > 0:
            self.converterMessage.emit('正在转换图片标注...', self.MessageType.Information)
            self.multiprocessConvertFlag.emit(0)
            pool = mul.Pool(processes=os.cpu_count())
            imgs = pool.starmap_async(
                self.convert_annotation_single,
                [img for img in image_to_convert]).get()
            pool.close()
            pool.join()
            self.multiprocessConvertFlag.emit(100)
            self.converterMessage.emit('正在向数据集内添加图片标注...', self.MessageType.Information)
            self.buildAnnotationMilestone.emit(0)
            for i in range(totoal_images_to_convert):
                self.dataset.add(imgs[i])
                self.buildAnnotationMilestone.emit(math.floor((i + 1) / (totoal_images_to_convert / 100)))
        return True

    def output(self):
        """
        Convert dataset to COCO format annotations
        :param fld: valid pathlib.Path object or path string
        :param mode: convert mode, can be cls.ConvertMode.{New | Merge | Overwrite} or integer {1 | 2 | 3}
        :return status: True if successful else False
        """
        annotation_path = (self.workFld / 'label') / 'annotations.json'
        if annotation_path.exists():
            if (self.mode == self.ConvertMode.Merge
                    and self.dataset._merged != annotation_path) \
                    or (self.mode == self.ConvertMode.New):
                os.rename(
                    annotation_path,
                    (self.workFld / 'label') / 'annotations_{tme}.json'.format(tme=datetime.now().strftime('%H%M%S'))
                )
        try:
            if not (self.workFld / 'label').exists():
                os.makedirs(self.workFld / 'label')
            with open(annotation_path, 'w') as f:
                self.converterMessage.emit('正在生成COCO格式标注文件...', self.MessageType.Information)
                json.dump(self.dataset.coco(), f)
        except (PermissionError, TypeError) as e:
            self.converterMessage.emit(
                '无法写入"{ant}"'.format(ant=str(annotation_path)),
                self.MessageType.Critical
            )
            return False
        return True

    def convert_annotations_append(self, imgPaths):
        total_ImageToConvert = len(imgPaths)
        annotation_path = (imgPaths[0].parent / 'label') / 'annotations.json'
        with open(annotation_path, 'r') as _anno:
            annotations = json.load(_anno)

        dataset = Dataset.from_coco(annotations, name='Slag dataset', config=self.config)

        category = dataset.categories.get('slag')
        if not category:  # if category('slag') not found, set annotations to first category in dataset
            category = next(iter(dataset.categories.values()))

        self.converterMessage.emit('正在转换选择的图片...', self.MessageType.Information)
        self.buildAnnotationMilestone.emit(0)
        for img_idx, imgPath in enumerate(imgPaths):
            imageFound = 0
            for img_id, img in dataset.images.items():
                if img.file_name == imgPath.name:
                    image = img
                    imageFound = img_id
            if not imageFound:
                imageFound = len(dataset.images) + 1
                image = self.convert_annotation_single(imageFound, imgPath, category, config=self.config)
                dataset.add(image)
            else:
                image.annotations = {}  # clear the annotation dictionary to prevent duplicate insertion
                image = self.convert_annotation_single(imageFound, imgPath, category, config=self.config, img_object=image)
                annotationToAdd = []
                for annotation in image.annotations.values():
                    annotationToAdd.append(annotation)
                for annotation in annotationToAdd:
                    dataset.add(annotation)
            self.buildAnnotationMilestone.emit(math.floor((img_idx + 1) / (total_ImageToConvert / 100)))

        try:
            with open(annotation_path, 'w') as _anno:
                self.converterMessage.emit('正在生成COCO格式标注文件...', self.MessageType.Information)
                json.dump(dataset.coco(), _anno)
        except (PermissionError, TypeError) as e:
            self.converterMessage.emit(
                '无法写入"{ant}"'.format(ant=str(annotation_path)),
                self.MessageType.Critical
            )
            return False
        return True

    def repairAnnotation(self, fld):
        if not isinstance(fld, Path):
            fld = Path(fld)
        if fld.is_file():
            annotation_path = fld
            new_image_root = fld.parent.parent.as_posix()
        else:
            annotation_path = (fld / 'label') / 'annotations.json'
            new_image_root = fld.as_posix()
        if not annotation_path.exists():
            return False
        try:
            with open(annotation_path, 'r') as _anno:
                annotations = json.load(_anno)

            old_image_root = annotations['info']['image_root']
            total_images = len(annotations['images'])
            self.converterMessage.emit('正在修复标注文件...', self.MessageType.Information)
            self.buildAnnotationMilestone.emit(0)
            for i in range(total_images):
                annotations['images'][i]['path'] = replace_absolute_image_path(
                    annotations['images'][i]['path'],
                    old_image_root,
                    new_image_root
                )
                self.buildAnnotationMilestone.emit(math.floor((i + 1) / (total_images / 100)))
            annotations['info']['image_root'] = new_image_root
        except Exception:
            self.converterMessage.emit(
                '无法读取"{ant}", 或包含非法键值'.format(ant=str(annotation_path)),
                self.MessageType.Critical
            )
            return False
        try:
            with open(annotation_path, 'w') as _anno:
                json.dump(annotations, _anno)
        except (PermissionError, TypeError) as e:
            self.converterMessage.emit(
                '无法写入"{ant}"'.format(ant=str(annotation_path)),
                self.MessageType.Critical
            )
            return False
        return True

    def mergeAnnotation(self, source, target, sourceLib=None):
        with open(source, 'r') as f:
            source_anno = json.load(f)
        with open(target, 'r') as f:
            target_anno = json.load(f)

        if not sourceLib: # rebuild source mapping table
            sourceLib = {}
            imgCount = 0
            annoCount = 0
            totalImageCount = len(source_anno['images'])
            totalAnnotationCount = len(source_anno['annotations'])
            self.converterMessage.emit('正在重建源文件索引...', self.MessageType.Information)
            self.buildAnnotationMilestone.emit(0)
            for img in source_anno['images']:
                imgID = img['id']
                imgDict = {}
                imgDict['annotation_map'] = set()
                sourceLib[imgID] = imgDict
                imgCount += 1
                self.buildAnnotationMilestone.emit(math.floor(imgCount / (totalImageCount / 100)))
            self.buildAnnotationMilestone.emit(0)
            for anno in source_anno['annotations']:
                annoID = anno['id']
                sourceLib[anno['image_id']]['annotation_map'].add(annoID)
                annoCount += 1
                self.buildAnnotationMilestone.emit(math.floor(annoCount / (totalAnnotationCount / 100)))

        source_cat_set = set()
        source_cat_inv_map = {}
        target_cat_set = set()
        target_cat_id_set = set()
        source_cat_id_map = {}
        catCount = 0
        for cat in source_anno['categories']:
            source_cat_set.add(cat['name'].lower()) # use category name as criterion, omit difference in category colors
            source_cat_inv_map[cat['name'].lower()] = catCount
            catCount += 1
        for cat in target_anno['categories']:
            target_cat_set.add(cat['name'].lower())
            target_cat_id_set.add(cat['id'])
        source_cat_to_merge = source_cat_set - source_cat_set.intersection(target_cat_set)  # remove duplicates categories
        cur_cat_id = 1
        for cat in source_cat_to_merge:
            cat_to_merge = source_anno['categories'][source_cat_inv_map[cat]]
            while cur_cat_id in target_cat_id_set:
                cur_cat_id += 1
            source_cat_id_map[cat_to_merge['id']] = cur_cat_id
            cat_to_merge['id'] = cur_cat_id
            target_anno['categories'].append(cat_to_merge)
            cur_cat_id += 1

        source_img_set = set()
        source_inv_map = {}
        target_img_set = set()
        target_img_id_set = set()
        target_anno_id_set = set()
        imgCount = 0
        for img in source_anno['images']:
            source_img_set.add(img['file_name']) # for set intersection
            source_inv_map[img['file_name']] = imgCount # mapping image filename to source index
            imgCount += 1
        for img in target_anno['images']:
            target_img_set.add(img['file_name']) # for set intersection
            target_img_id_set.add(img['id']) # get target image ids for index
        for anno in target_anno['annotations']:
            target_anno_id_set.add(anno['id']) # get target annotation ids for index
        source_img_to_merge = source_img_set - source_img_set.intersection(target_img_set) # remove duplicates images
        cur_img_id = 1
        cur_anno_id = 1

        self.converterMessage.emit('正在合并标注文件...', self.MessageType.Information)
        self.buildAnnotationMilestone.emit(0)
        imgCount = 0
        totalImageCount = len(source_img_to_merge)
        # main loop for image
        for img_name in source_img_to_merge:
            while cur_img_id in target_img_id_set:
                cur_img_id += 1 # search for minimum available image id

            img_to_merge = source_anno['images'][source_inv_map[img_name]] # retrieve source image record
            anno_id_to_merge = sourceLib[img_to_merge['id']]['annotation_map'] # retrieve source annotation ids corresponding to the image
            anno_to_merge_list = [] # initialize a list to store source annotation records to merge

            for anno in source_anno['annotations']: # traverse source annotations to find record with specified id
                if anno['id'] in anno_id_to_merge:
                    anno_to_merge_list.append(anno)

            for anno in anno_to_merge_list:
                source_anno['annotations'].pop(source_anno['annotations'].index(anno)) # delete merged source annotations records to avoid repetitive searching

            # sub loop for annotation
            for anno in anno_to_merge_list:
                while cur_anno_id in target_anno_id_set:
                    cur_anno_id += 1 # search for minimum available annotation id

                anno['id'] = cur_anno_id # change source annotation id for merging
                anno['image_id'] = cur_img_id # change corresponding image id
                anno['category_id'] = source_cat_id_map.get(anno['category_id'], anno['category_id']) # change corresponding category id
                target_anno['annotations'].append(anno) # merge

                cur_anno_id += 1 # try to find next available annotation id

            img_to_merge['id'] = cur_img_id  # change source image id for merging
            target_anno['images'].append(img_to_merge)  # merge

            cur_img_id += 1 # try to find next available image id
            imgCount += 1
            self.buildAnnotationMilestone.emit(math.floor(imgCount / (totalImageCount / 100)))

        return target_anno

    def folderCompatibilityCheck(self, fld):
        if not isinstance(fld, Path):
            fld = Path(fld)
        resultFld = fld / 'result'
        imgPaths = [f for f in fld.glob('*.jpg')]
        fldImageCount = len(imgPaths)
        _resultFldExists = resultFld.exists()
        if _resultFldExists:
            maskPaths = [f for f in resultFld.glob('*.tif')]
            maskCount = len(maskPaths)
            if fldImageCount != maskCount:  # 检查数量是否匹配
                return False, False
            if fldImageCount > 0:  # maskCount也大于0
                for imgPath in imgPaths:  # 逐个检查文件名是否匹配
                    if not (resultFld / (imgPath.stem + '.border.tif')).exists():
                        return False, False
                return False, True # 非空合法目录
        if fldImageCount > 0:  # 目录非空
            return False, False  # result文件夹不存在，目录不合法
        return True, True  # 空合法目录

    def annotationCompatibilityCheck(self, fld, category_name, send_message = True):
        if not isinstance(fld, Path):
            fld = Path(fld)
        if fld.is_file():
            annotation_path = fld
        else:
            annotation_path = (fld / 'label') / 'annotations.json'
        if not annotation_path.exists():
            return self.ConvertModeFlag.New
        try:
            with open(annotation_path, 'r') as _anno:
                annotations = json.load(_anno)
        except json.decoder.JSONDecodeError as e:
            if send_message:
                self.converterMessage.emit(
                    '无法读取"{ant}", 采用覆写模式'.format(ant=str(annotation_path)),
                    self.MessageType.Warning
                )
            return self.ConvertModeFlag.Overwrite

        _imgRootMismatch = False
        _imgNameMismatch = False

        image_names = set([path.name for path in fld.glob('*.jpg')])
        total_images = len(image_names)
        try:
            # category存在性检查
            _categoryFound = 0 # annotation中没有slag的category
            for i in range(1, len(annotations['categories']) + 1):
                if annotations['categories'][i - 1]['name'].lower() == category_name.lower():
                    _categoryFound = i

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
            if send_message:
                self.converterMessage.emit(
                    '"{ant}"缺失关键键值, 采用覆写模式'.format(ant=str(annotation_path)),
                    self.MessageType.Warning
                )
            return self.ConvertModeFlag.Overwrite

        if _imgCountMismatch > 0 or _imgNameMismatch:
            if send_message:
                self.converterMessage.emit(
                    '文件夹中现有标注文件与图片数据不符, 不可进行合并，请选择新建或覆写模式',
                    self.MessageType.Warning
                )
            return self.ConvertModeFlag.New | self.ConvertModeFlag.Overwrite | self.ConvertModeFlag.Extractable

        message = '目标文件夹存在以下问题:'
        if not _categoryFound:
            message += '\n- 未在已有标注文件中发现目标分类, 可能由于标注文件由其他来源生成, 建议采用新建或覆写模式, 或检查后再进行合并'
        if _imgCountMismatch < 0:
            message += '\n- 文件夹中存在尚未转化的原始图像'
        if _imgRootMismatch:
            message += '\n- 已有标注文件的图片根目录与目标文件夹不一致, 可能由于文件移动或跨平台导致, 需要进行修复'
        if _imgCountMismatch < 0 or _imgRootMismatch or not _categoryFound:
            if send_message:
                self.converterMessage.emit(
                    message,
                    self.MessageType.Warning
                )
        return self.ConvertModeFlag.Merge | self.ConvertModeFlag.Extractable | (
            self.ConvertModeFlag.NeedRepair if _imgRootMismatch else self.ConvertModeFlag.NoFlag
        ) | (
            self.ConvertModeFlag.New if not _categoryFound else self.ConvertModeFlag.NoFlag
        ) | (self.ConvertModeFlag.Overwrite if not _categoryFound else self.ConvertModeFlag.NoFlag)
        # Case1: _imgRootMismatch=False, imgCountMismatch=0, _imgNameMismatch=0
        #        means fully compatible annotation, can only merge
        # Case2: _imgRootMismatch=True, imgCountMismatch=0, _imgNameMismatch=0
        #        means fully compatible annotation but has position moved or generated by other platform,
        #        can merge after repair or overwrite
        # Case3: _imgRootMismatch=False, imgCountMismatch<0, _imgNameMismatch=0
        #        means partially compatible annotation with image(s) left unconverted,
        #        can only merge
        # Case4: _imgRootMismatch=True, imgCountMismatch<0, _imgNameMismatch=0
        #        means partially compatible annotation with image(s) left unconverted and need to be repair,
        #        can merge after repair or overwrite
        # Case5: _imgRootMismatch=False, imgCountMismatch>0, _imgNameMismatch=imgCountMismatch
        #        means partially incompatible annotation with image(s) missing,
        #        can merge after remove redundant record(s) or overwrite, but removing may be time consuming so suggest to overwrite
        # Case6: _imgRootMismatch=True, imgCountMismatch>0, _imgNameMismatch=imgCountMismatch
        #        means partially compatible annotation with image(s) missing and position changed,
        #        can merge after remove redundant record(s) and repair or overwrite, but removing may be time consuming so suggest to overwrite

        # Step1: Check if imgCountMismatch>0, missing original image(s), new or overwrite
        # Step2: Check if _imgNameMismatch>0, missing original image(s), new or overwrite
        # Step3: Check if _imgRootMismatch to determine the necessary to repair


if __name__ == '__main__':
    a = QAnnotationConverter()
    # fld = Path(r'd:\pythondata\PyTorch\data\slag_simple')
    fld = Path(r'/mnt/WinD/pythondata/PyTorch/data/slag_simple')
    # _empty, _compat = a.folderCompatibilityCheck(fld)
    # a.build_dataset(fld, a.ConvertMode.New, 'Slag', (244, 108, 59))
    # a.convert_annotations()
    # a.output()
    anno1 = Path('/mnt/WinD/pythondata/PyTorch/data/test1/label/annotations_temp.json')
    anno2 = Path('/mnt/WinD/pythondata/PyTorch/data/test1/label/annotations.json')
    anno_combine = a.mergeAnnotation(anno1, anno2)
    with open(anno2.parent / 'annotations_combine.json', 'w') as f:
        json.dump(anno_combine, f)


    ii=0