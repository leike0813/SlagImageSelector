import os
from pathlib import Path
import datetime
import re
import math
import shutil
import json
from enum import IntFlag
from enum import IntEnum
import PIL.Image as PILImg
import numpy as np
import pandas as pd
import PySide2.QtCore as QtC
from lib.parameterizedImantics import Default_Config
from lib.parameterizedImantics.utils import replace_absolute_image_path
from lib.utils import QAnnotationConverter
from lib.utils import QThumbnailConverter


__all__ = ['IOWorker']


class IOWorker(QtC.QObject):
    class MessageType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    workerException = QtC.Signal(Exception)
    workerMessage = QtC.Signal(str, int)
    sendToListWidget = QtC.Signal(str)
    sendToProgressBar = QtC.Signal(int)
    sendToProgressBarRange = QtC.Signal(int, int)
    sendSelected = QtC.Signal(int)

    imageLibLoaded = QtC.Signal(int, pd.DataFrame)
    dataLoaded = QtC.Signal(int)
    annotationRepaired = QtC.Signal(Path, IntFlag)
    exportFinished = QtC.Signal(Path, int)
    convertFinished = QtC.Signal(bool)
    annotationOpened = QtC.Signal(dict)
    annotationExtracted = QtC.Signal(bool)
    selectionSaved = QtC.Signal(bool)
    thumbnailCached = QtC.Signal(Path, list, set, float)

    def __init__(self, mainWindow, parent=None):
        super(IOWorker, self).__init__(parent)
        self.mainWindow = mainWindow
        self.imanticsConfig = Default_Config.clone()
        # self.imanticsConfig.IMAGE.USE_RELATIVE_PATH = True
        self.annotationConverter = QAnnotationConverter(config=self.imanticsConfig, parent=self)
        self.thumbnailConverter = QThumbnailConverter(parent=self)
        self.creationTimeRegExp = r'^_([0-9]{6})_([0-9]{9})'

        self.annotationConverter.converterMessage.connect(self.converterMessageProxy)
        self.annotationConverter.buildAnnotationMilestone.connect(self.converterProgressProxy) # for singlethread compatibility
        self.annotationConverter.multiprocessConvertFlag.connect(lambda maxprog: self.converterProgressRangeProxy(0, maxprog))
        self.thumbnailConverter.converterMessage.connect(self.converterMessageProxy)
        self.thumbnailConverter.convertThumbnailMilestone.connect(self.converterProgressProxy)

    @QtC.Slot(Path)
    def onDataFolderOpened(self, workFld):
        try:
            origImagePaths = [f for f in workFld.glob('*.jpg')]
            origImageCount = len(origImagePaths)
            resultFld = workFld / 'result'
            imageLib = pd.DataFrame(columns=[
                'Orig_Image', 'Creation_Time'])
            imgCount = 0
            self.sendToProgressBar.emit(0)
            for imgPath in origImagePaths:
                timeStr = re.findall(self.creationTimeRegExp, imgPath.name)
                if (resultFld / imgPath.name).exists():
                    imageLib.loc[imgCount] = [
                        imgPath.name,
                        datetime.datetime.strptime(timeStr[0][0] + timeStr[0][1], '%y%m%d%H%M%S%f'),
                    ]
                    self.sendToListWidget.emit(imgPath.name)
                    imgCount += 1
                    self.sendToProgressBar.emit(math.floor(imgCount / (origImageCount / 100)))
            self.imageLibLoaded.emit(imgCount, imageLib)
            if (workFld / 'selected.json').exists():
                try:
                    with open(workFld / 'selected.json', 'r') as f:
                        json_obj = json.load(f)
                    selection = json_obj['selected']
                    cur_idx = json_obj['cursor']
                    for sel in selection:
                        self.sendSelected.emit(list(imageLib['Orig_Image']).index(sel))
                    self.dataLoaded.emit(cur_idx)
                except (KeyError, json.JSONDecodeError):
                    self.dataLoaded.emit(0)
            else:
                self.dataLoaded.emit(0)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, IntFlag)
    def onRepairAnnotationRequestReceived(self, exportFld, convertFlag):
        try:
            if self.annotationConverter.ConvertModeFlag.NeedRepair in convertFlag:
                self.annotationConverter.repairAnnotation(exportFld)
                convertFlag ^ self.annotationConverter.ConvertModeFlag.NeedRepair
                self.workerMessage.emit('标注文件修复完成', self.MessageType.Information)
            self.annotationRepaired.emit(exportFld, convertFlag)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, Path, list, pd.DataFrame, int)
    def onExportFolderOpened(self, exportFld, workFld, outputList, imageLib, convertMode):
        try:
            if not (exportFld / 'result').exists():
                os.makedirs(exportFld / 'result')
            total_ExportImages = len(outputList)
            self.workerMessage.emit('正在导出选择集...', self.MessageType.Information)
            self.sendToProgressBar.emit(0)
            for i in range(total_ExportImages):
                imgInfo = imageLib.loc[outputList[i]]
                imgPath = workFld / imgInfo['Orig_Image']
                maskPath = (workFld / 'result') / (imgPath.stem + '.border.tif')
                convertName = imgInfo['Creation_Time'].isoformat(timespec='milliseconds').replace(':', '-')
                exportImgPath = exportFld / (convertName + '.jpg')
                exportMaskPath = (exportFld / 'result') / (convertName + '.border.tif')
                if not exportImgPath.exists():
                    shutil.copy(imgPath, exportImgPath)
                if not exportMaskPath.exists():
                    shutil.copy(maskPath, exportMaskPath)
                self.sendToProgressBar.emit(math.floor((i + 1) / (total_ExportImages / 100)))
            self.exportFinished.emit(exportFld, convertMode)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, int)
    def onConvertAnnotationRequestReceived(self, targetFld, convertMode):
        try:
            status = self.annotationConverter.build_dataset(
                targetFld, convertMode, category_name='Slag', category_color=(244, 108, 59),
                category_id=1, dataset_name='Slag dataset',
            )
            if not status:
                self.workerMessage.emit('构建数据集过程中发生错误', self.MessageType.Critical)
            status = self.annotationConverter.convert_annotations()
            if not status:
                self.workerMessage.emit('转换图片标注过程中发生错误', self.MessageType.Critical)
            status = self.annotationConverter.output()
            if not status:
                self.workerMessage.emit('导出COCO格式标注文件过程中发生错误', self.MessageType.Critical)
            self.workerMessage.emit('转换完成', self.MessageType.Information)
            self.convertFinished.emit(True)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(list)
    def onConvertSingleImageAnnotationRequestReceived(self, imgPaths):
        try:
            if not ((imgPaths[0].parent / 'label') / 'annotations.json').exists():
                self.workerMessage.emit('未找到现有标注文件, 文件可能已删除/移动或更名', self.MessageType.Critical)
                self.convertFinished.emit(True)
                return False
            status = self.annotationConverter.convert_annotations_append(imgPaths)
            if not status:
                self.workerMessage.emit('转换图片标注过程中发生错误', self.MessageType.Critical)
            self.workerMessage.emit('转换完成', self.MessageType.Information)
            self.convertFinished.emit(True)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path)
    def onOpenAnnotationRequestReceived(self, sourceFile):
        try:
            with open(sourceFile, 'r') as _anno:
                annotations = json.load(_anno)

            imageLib = {}
            imgCount = 0
            annoCount = 0
            totalImageCount = len(annotations['images'])
            totalAnnotationCount = len(annotations['annotations'])
            self.workerMessage.emit('正在分析文件中的图片信息...', self.MessageType.Information)
            self.sendToProgressBar.emit(0)
            for img in annotations['images']:
                imgID = img['id']
                imgPath = Path(img['path'])
                boundaryPath = (imgPath.parent / 'result') / (imgPath.stem + '.border.tif')
                imgDict = {}
                imgDict['file_name'] = img['file_name']
                imgDict['path'] = imgPath
                imgDict['boundary_path'] = boundaryPath
                imgDict['annotation_map'] = set()

                if imgPath.exists():
                    thumbFld = imgPath.parent / '.thumbnail'
                    if not thumbFld.exists():
                        os.makedirs(thumbFld)
                    if not (thumbFld / imgPath.name).exists():
                        ret, status = self.thumbnailConverter.convertThumbnail(imgPath, thumbFld)
                        if not status:
                            self.workerMessage.emit('{imgname}缩略图转换过程中发生错误', self.MessageType.Information)
                            imgDict['thumbnail_path'] = None
                        else:
                            imgDict['thumbnail_path'] = ret
                    else:
                        imgDict['thumbnail_path'] = thumbFld / imgPath.name
                else:
                    imgDict['thumbnail_path'] = None
                if boundaryPath.exists():
                    imgBoundaryArray = np.array(PILImg.open(boundaryPath), dtype=np.uint16)
                    imgDict['num_slag_in_orig_boundary'] = np.max(imgBoundaryArray)
                else:
                    imgDict['num_slag_in_orig_boundary'] = -1
                imageLib[imgID] = imgDict
                imgCount += 1
                self.sendToProgressBar.emit(math.floor(imgCount / (totalImageCount / 100)))

            self.workerMessage.emit('正在分析文件中的标注信息...', self.MessageType.Information)
            self.sendToProgressBar.emit(0)
            for anno in annotations['annotations']:
                annoID = anno['id']
                imageLib[anno['image_id']]['annotation_map'].add(annoID)
                annoCount += 1
                self.sendToProgressBar.emit(math.floor(annoCount / (totalAnnotationCount / 100)))
            self.annotationOpened.emit(imageLib)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, Path, dict)
    def onExtractAnnotationRequestReceived(self, sourceFile, targetFld, extractLib):
        try:
            with open(sourceFile, 'r') as f:
                sourceAnnotation = json.load(f)

            targetAnnotationPath = (targetFld / 'label') / 'annotations.json'
            annotationExist = targetAnnotationPath.exists()

            sourceImageInvMap = {}
            sourceAnnotationInvMap = {}
            imgCount = 0
            annoCount = 0
            for img in sourceAnnotation['images']:
                sourceImageInvMap[img['id']] = imgCount
                imgCount += 1
            for anno in sourceAnnotation['annotations']:
                sourceAnnotationInvMap[anno['id']] = annoCount
                annoCount += 1

            newAnnotation = {}
            newAnnotation['info'] = sourceAnnotation['info']
            newAnnotation['categories'] = sourceAnnotation['categories']
            newAnnotation['images'] = []
            newAnnotation['annotations'] = []
            currentImageID = 1
            currentAnnotationID = 1
            self.workerMessage.emit('正在提取并转存标注信息...', self.MessageType.Information)
            self.sendToProgressBar.emit(0)
            imgCount = 0
            totalImageCount = len(sourceAnnotation['images'])
            for img in sourceAnnotation['images']:
                if img['id'] in extractLib.keys():
                    imageToExtract = sourceAnnotation['images'][sourceImageInvMap[img['id']]]
                    imgPath = extractLib[img['id']]['path']
                    boundaryPath = extractLib[img['id']]['boundary_path']
                    extractImgPath = Path(replace_absolute_image_path(imgPath, sourceAnnotation['info']['image_root'],
                                                                 targetFld.as_posix()))
                    extractBoundaryPath = Path(replace_absolute_image_path(boundaryPath,
                                                                      sourceAnnotation['info']['image_root'],
                                                                      targetFld.as_posix()))
                    if not extractImgPath.exists():
                        shutil.copy(imgPath, extractImgPath)
                    if not extractBoundaryPath.exists():
                        if not (targetFld / 'result').exists():
                            os.makedirs(targetFld / 'result')
                        shutil.copy(boundaryPath, extractBoundaryPath)

                    imageToExtract['path'] = extractImgPath.as_posix()

                    for anno_id in extractLib[img['id']]['annotation_map']:
                        annotationToMerge = sourceAnnotation['annotations'][sourceAnnotationInvMap[anno_id]]
                        if not annotationExist:
                            annotationToMerge['image_id'] = currentImageID
                            annotationToMerge['id'] = currentAnnotationID
                        newAnnotation['annotations'].append(annotationToMerge)
                        currentAnnotationID += 1
                    if not annotationExist:
                        imageToExtract['id'] = currentImageID
                    newAnnotation['images'].append(imageToExtract)
                    currentImageID += 1
                imgCount += 1
                self.sendToProgressBar.emit(math.floor(imgCount / (totalImageCount / 100)))

            newAnnotation['info']['image_root'] = targetFld.as_posix()

            if annotationExist:
                with open(targetAnnotationPath.parent / 'annotations_temp.json', 'w') as f:
                    json.dump(newAnnotation, f)

                newAnnotation = self.annotationConverter.mergeAnnotation(targetAnnotationPath.parent / 'annotations_temp.json', targetAnnotationPath, extractLib)
                os.remove(targetAnnotationPath.parent / 'annotations_temp.json')
            else:
                if not (targetFld / 'label').exists():
                    os.makedirs(targetFld / 'label')

            with open(targetAnnotationPath, 'w') as f:
                json.dump(newAnnotation, f)

            self.workerMessage.emit('提取完成', self.MessageType.Information)
            self.annotationExtracted.emit(True)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, list, pd.DataFrame, int)
    def onSaveRequestReceived(self, workFld, outputList, imageLib, cur_idx, exitAfterSaved):
        try:
            selection = [imageLib.loc[i]['Orig_Image'] for i in outputList]
            with open(workFld / 'selected.json', 'w') as f:
                json.dump({'selected': selection, 'cursor': cur_idx}, f)
            self.selectionSaved.emit(exitAfterSaved)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(Path, list, pd.DataFrame)
    def onSelectionViewRequestReceived(self, workFld, outputList, imageLib):
        try:
            imageNames = [imageLib.loc[i]['Orig_Image'] for i in outputList]
            thumbnailScale, invalidImages = self.thumbnailConverter.cacheThumbnail(workFld, imageNames)
            self.thumbnailCached.emit(workFld, imageNames, invalidImages, thumbnailScale)
            self.workerMessage.emit('', self.MessageType.Information)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(str, int)
    def converterMessageProxy(self, msg, msgtype):
        self.workerMessage.emit(msg, msgtype)

    @QtC.Slot(int)
    def converterProgressProxy(self, prog):
        self.sendToProgressBar.emit(prog)

    @QtC.Slot(int, int)
    def converterProgressRangeProxy(self, minimum, maximum):
        self.sendToProgressBarRange.emit(minimum, maximum)