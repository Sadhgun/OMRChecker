from src.processors.manager import PROCESSOR_MANAGER
from src.core import ImageInstanceOps
import cv2
from src.defaults import CONFIG_DEFAULTS
from src.utils.image import ImageUtils
import os

def Cropper(image, dest):
        config = CONFIG_DEFAULTS
        config.outputs.show_image_level = 6
        image_instance_ops = ImageInstanceOps(config)
        marker = "required-files/omr_marker.jpg"
        img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        img = ImageUtils.resize_util(img, CONFIG_DEFAULTS.dimensions.processing_width, CONFIG_DEFAULTS.dimensions.processing_height)
        ProcessorClass = PROCESSOR_MANAGER.processors["CropOnMarkers"]
        pre_processor_instance = ProcessorClass(
                        options={"relativePath": "omr_marker.jpg",
                                "sheetToMarkerWidthRatio": 16},
                        relative_dir="required-files",
                        image_instance_ops=image_instance_ops,)
        
        new = pre_processor_instance.apply_filter(image=img, file_path=marker)
        if new is not None:
                cv2.imwrite(filename=dest, img=new)
                os.remove(image)
                return True
        else:
                return False
