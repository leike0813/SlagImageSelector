# -*- coding: utf-8 -*-
import os
import sys
import math
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from PIL import Image as PILImg
import json
import numpy as np
import cv2
import PySide2.QtCore as QtC


__all__ = ['QThumbnailConverter']


class QThumbnailConverter(QtC.QObject):
    class MessageType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    converterMessage = QtC.Signal(str, int)
    convertThumbnailMilestone = QtC.Signal(int)

    def __init__(self, parent=None):
        super(QThumbnailConverter, self).__init__(parent)
        self.cached = set()

    def cacheThumbnail(self, fld, imageNames=None, thumbnailScale=0.1):
        try:
            thumbFld = fld / '.thumbnail'
            if not thumbFld.exists():
                os.makedirs(thumbFld)
            if not imageNames:
                imagePaths = [f for f in fld.glob('*.jpg')]
            else:
                imagePaths = [Path(fld / name) for name in imageNames]
            imageToCache = []
            invalidImages = set()
            for path in imagePaths:
                if not path.exists():
                    # self.converterMessage.emit('{imgpath}不存在'.format(imgpath=str(path)), self.MessageType.Information)
                    invalidImages.add(path)
                    continue
                if path not in self.cached:
                    if (thumbFld / path.name).exists():
                        self.cached.add(path)
                        continue
                    imageToCache.append(path)
            total_ImageToCache = len(imageToCache)
            self.converterMessage.emit('正在生成缩略图...', self.MessageType.Information)
            self.convertThumbnailMilestone.emit(0)
            for imgIdx, imgPath in enumerate(imageToCache):
                # img = cv2.imread(imgPath.as_posix())
                # imgSize = img.shape
                # thumb = cv2.resize(img, (int(imgSize[1] * thumbnailScale), int(imgSize[0] * thumbnailScale)))
                # cv2.imwrite((thumbFld / imgPath.name).as_posix(), thumb)
                ret, status = self.convertThumbnail(imgPath, thumbFld, thumbnailScale)
                if status:
                    self.cached.add(imgPath)
                    self.convertThumbnailMilestone.emit(math.floor((imgIdx + 1) / (total_ImageToCache / 100)))
                else:
                    raise ret
            if len(invalidImages) > 0:
                self.converterMessage.emit(
                    '选择集中{num}张图片未能成功生成缩略图'.format(num=len(invalidImages)),
                    self.MessageType.Warning
                )
            return thumbnailScale, invalidImages
        except Exception as e:
            self.converterMessage.emit('生成缩略图过程中发生错误', self.MessageType.Warning)
            invalidImages = set(imagePaths) - self.cached
            # raise e
            return thumbnailScale, invalidImages

    @staticmethod
    def convertThumbnail(imagePath, outputFld=None, thumbnailScale=0.1):
        if not isinstance(imagePath, Path):
            imagePath = Path(imagePath)
        if not isinstance(outputFld, Path):
            outputFld = Path(outputFld)
        if not outputFld or outputFld == imagePath.parent:
            outputFld = imagePath.parent / '.thumbnail'

        # if not outputFld.exists(): # disable auto-creation of thumbnail directory to prevent misoperation,
        #     os.makedirs(outputFld) # make sure the .thumbnail directory is already exists before calling this method
        try:
            img = cv2.imread(imagePath.as_posix())
            imgSize = img.shape
            thumb = cv2.resize(img, (int(imgSize[1] * thumbnailScale), int(imgSize[0] * thumbnailScale)))
            cv2.imwrite((outputFld / imagePath.name).as_posix(), thumb)
            return outputFld / imagePath.name, True
        except Exception as e:
            return e, False