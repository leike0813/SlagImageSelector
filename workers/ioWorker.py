import os
import warnings
from io import BytesIO
import hashlib
from pathlib import Path
import datetime
import re
import math
import shutil
import json
from enum import IntFlag
from enum import IntEnum
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
    askForOverwrite = QtC.Signal(str)
    selectionSaved = QtC.Signal(bool)
    thumbnailCached = QtC.Signal(Path, list, set, float)

    def __init__(self, mainWindow, mutex=QtC.QMutex(), waitConditions={}, parent=None):
        super(IOWorker, self).__init__(parent)
        self.mainWindow = mainWindow
        self.mutex = mutex
        self.waitConditions = waitConditions
        self.imanticsConfig = Default_Config.clone()
        # self.imanticsConfig.IMAGE.USE_RELATIVE_PATH = True
        self.annotationConverter = QAnnotationConverter(config=self.imanticsConfig, parent=self)
        self.thumbnailConverter = QThumbnailConverter(parent=self)
        self.creationTimeRegExp = r'^_([0-9]{6})_([0-9]{9})'
        # self.backupCreationTimeRegExp = r'^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2})-([0-9]{2})-([0-9]{2}).([0-9]{3})'

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
                if len(timeStr) == 0:
                    # timeStr = re.findall(self.backupCreationTimeRegExp, imgPath.name)
                    # timeStr = [(
                    #     timeStr[0][0][2:] + timeStr[0][1] + timeStr[0][2],
                    #     timeStr[0][3] + timeStr[0][4] + timeStr[0][5] + timeStr[0][6]
                    # )]
                    self.workerMessage.emit('请选择正确的原始数据文件夹', self.MessageType.Critical)
                    self.workerMessage.emit('', self.MessageType.Information)
                    return
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

            annoDataDict = self.annotationConverter.anno_dict2pd(annotations)
            self.thumbnailConverter.cacheThumbnail(Path(annoDataDict['info']['image_root']))
            annoDataDict['images'] = self.annotationConverter.extendImageLib(annoDataDict['images'], annoDataDict['annotations'])

            self.annotationOpened.emit(annoDataDict)
        except Exception as e:
            self.workerException.emit(e)

    @QtC.Slot(dict, Path, set)
    def onExtractAnnotationRequestReceived(self, annoDataDict, targetFld, selection):
        try:
            targetAnnotationPath = (targetFld / 'label') / 'annotations.json'
            annotationExist = targetAnnotationPath.exists()

            imageAnnotationPath = (targetFld / 'label') / 'image_annotations'
            if not imageAnnotationPath.exists():
                os.makedirs(imageAnnotationPath)

            source_annotation_group = annoDataDict['annotations'].groupby(annoDataDict['annotations'].image_id)
            extractDataDict = {
                'info': annoDataDict['info'],
                'categories': pd.DataFrame(columns=annoDataDict['categories'].columns),
                'images': pd.DataFrame(columns=annoDataDict['images'].columns),
                'annotations': pd.DataFrame(columns=annoDataDict['annotations'].columns),
            }

            currentImageID = 1
            categoryIDSet = set()
            self.workerMessage.emit('正在提取并转存标注信息...', self.MessageType.Information)
            self.sendToProgressBar.emit(0)
            imgCount = 0
            totalImageCount = len(selection)
            overwriteSet = set()
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
                warnings.filterwarnings('ignore', category=FutureWarning)
                for imgIdx in selection:
                    img = annoDataDict['images'].iloc[imgIdx]
                    imgPath = img['Path']
                    boundaryPath = img['BoundaryPath']
                    extractImgPath = Path(replace_absolute_image_path(
                        imgPath,
                        annoDataDict['info']['image_root'],
                        targetFld.as_posix()
                    ))
                    extractBoundaryPath = Path(replace_absolute_image_path(
                        boundaryPath,
                        annoDataDict['info']['image_root'],
                        targetFld.as_posix()
                    ))
                    imgAnnoPath = imageAnnotationPath / (imgPath.stem + '.json')
                    if not extractImgPath.exists():
                        shutil.copy(imgPath, extractImgPath)
                    if not extractBoundaryPath.exists():
                        if not (targetFld / 'result').exists():
                            os.makedirs(targetFld / 'result')
                        shutil.copy(boundaryPath, extractBoundaryPath)

                    img['path'] = extractImgPath.as_posix()

                    anno = source_annotation_group.get_group(img['id'])
                    if not annotationExist:
                        anno['image_id'] = currentImageID
                        img['id'] = currentImageID

                    anno_dict = anno.to_dict(orient='index')
                    if not imgAnnoPath.exists():
                        with open(imgAnnoPath, 'w') as f:
                            json.dump(anno_dict, f)
                    else:
                        print(self.sha1Comparer(anno_dict, imgAnnoPath))
                        if not self.sha1Comparer(anno_dict, imgAnnoPath):
                            self.mutex.lock()
                            _applyForAllFlag = self.mainWindow._applyForAllFlag
                            if not _applyForAllFlag:
                                self.askForOverwrite.emit(imgPath.name)
                                self.waitConditions['AskForOverwrite'].wait(self.mutex)
                            _overwriteFlag = self.mainWindow._overwriteFlag
                            self.mutex.unlock()
                            if _overwriteFlag:
                                overwriteSet.add(imgPath.name)
                                with open(imgAnnoPath, 'w') as f:
                                    json.dump(anno_dict, f)

                    extractDataDict['images'].loc[imgCount] = img
                    extractDataDict['annotations'] = pd.concat([extractDataDict['annotations'], anno])
                    for _, anno_item in anno.iterrows():
                        categoryIDSet.add(anno_item['category_id'])
                    currentImageID += 1
                    imgCount += 1
                    self.sendToProgressBar.emit(math.floor(imgCount / (totalImageCount / 100)))

                if not annotationExist:
                    extractDataDict['annotations'].reset_index(drop=True, inplace=True)
                    extractDataDict['annotations']['id'] = extractDataDict['annotations'].index + 1

            self.mainWindow._overwriteFlag = False
            self.mainWindow._applyForAllFlag = False

            categoryIDSet = list(categoryIDSet)
            totalCategories = len(categoryIDSet)
            catIndexFrame = annoDataDict['categories'].set_index('id', drop=False)
            for i in range(totalCategories):
                extractDataDict['categories'].loc[i] = catIndexFrame.loc[categoryIDSet[i]]

            extractDataDict['info']['image_root'] = targetFld.as_posix()

            if annotationExist:
                with open(targetAnnotationPath, 'r') as f:
                    targetAnnotation = json.load(f)

                targetAnnotation = self.annotationConverter.anno_dict2pd(targetAnnotation)
                extractDataDict = self.annotationConverter.mergeAnnotation(extractDataDict, targetAnnotation, overwriteSet)
            else:
                extractDataDict['images'].drop(
                    columns=['Path', 'BoundaryPath', 'ThumbnailPath', 'NumSlagInOrigBoundary', 'AnnotationMap'],
                    inplace=True)
                if not (targetFld / 'label').exists():
                    os.makedirs(targetFld / 'label')

            with open(targetAnnotationPath, 'w') as f:
                json.dump(self.annotationConverter.anno_pd2dict(extractDataDict), f)

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


    @staticmethod
    def sha1Comparer(source_json_dict, target_file_path, block_size=64 * 1024):
        """
        :param source_json_dict: JSON serializable dictionary
        :param target_file_path: .json file
        """
        with open(target_file_path, 'rb') as target_io:
            sha1_target = hashlib.sha1()
            while True:
                target_data = target_io.read(block_size)
                if not target_data:
                    break
                sha1_target.update(target_data)

        source_io = BytesIO()
        source_io.write(json.dumps(source_json_dict).encode('utf-8'))
        source_io.seek(0)
        sha1_source = hashlib.sha1()
        while True:
            source_data = source_io.read(block_size)
            if not source_data:
                break
            sha1_source.update(source_data)

        return sha1_source.digest() == sha1_target.digest()