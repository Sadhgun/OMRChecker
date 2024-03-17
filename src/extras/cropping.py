from src.processors.manager import PROCESSOR_MANAGER
from src.core import ImageInstanceOps
import cv2
from src.defaults import CONFIG_DEFAULTS
from src.utils.image import ImageUtils

def Cropper(image, dest):
        config = CONFIG_DEFAULTS
        config.outputs.show_image_level = 6
        image_instance_ops = ImageInstanceOps(config)
        marker = "required-files/omr_marker.jpg"
        img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        img = ImageUtils.resize_util(img, 1332, 1640)
        ProcessorClass = PROCESSOR_MANAGER.processors["CropOnMarkers"]
        pre_processor_instance = ProcessorClass(
                        options={"relativePath": "omr_marker.jpg",
                                "sheetToMarkerWidthRatio": 7},
                        relative_dir="required-files",
                        image_instance_ops=image_instance_ops,)
        
        new = pre_processor_instance.apply_filter(image=img, file_path=marker)
        new = ImageUtils.resize_util(new, 747, 1089)
        cv2.imwrite(filename=dest, img=new)

if __name__ == "__main__":
    image = "add-files/OMR SHEET 6 001.png"
    dest = "add-files/OMR SHEET.png"
    Cropper(image, dest)