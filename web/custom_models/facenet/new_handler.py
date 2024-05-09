# custom handler file

# model_handler.py

"""
ModelHandler defines a custom model handler.
"""
import logging
import torch
import torch.nn.functional as F
import io
from PIL import Image
from torchvision import transforms
from ts.torch_handler.base_handler import BaseHandler
import numpy as np
import os
import zlib



class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self._context = None
        self.initialized = False
        self.model = None
        self.device = None

        self.img_preprocess = transforms.Compose([
    
            # 裁剪
            transforms.Resize((112,112)),
            # PIL图像转为tensor，归一化到[0,1]：Converts a PIL Image or numpy.ndarray (H x W x C) in the range [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0]
            transforms.ToTensor(),
            # 规范化至 [-1,1]
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            
        ])
       
    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        
        #  load the model, refer 'custom handler class' above for details
        #  load the model
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt file")

        self.model = torch.jit.load(model_pt_path)

        self.initialized = True
        


    def preprocess(self, data):
        """
        Transform raw input into model input data.
        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """
        # Take the input data and make it inference ready

        images = []

        for row in data:
            # Compat layer: normally the envelope should just return the data
            # directly, but older versions of Torchserve didn't have envelope.
            image = row.get("data") or row.get("body")

            image = Image.open(io.BytesIO(image))

            image = self.img_preprocess(image)

            images.append(image)

        return torch.stack(images).to(self.device)



    def inference(self, model_input):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output
        model_output = self.model.forward(model_input)
        return model_output

    def postprocess(self, inference_output):
        """
        Return inference result.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        # Take output from network and post-process to desired format

        res = []
        # pres has size [BATCH_SIZE, 1]
        # convert it to list
        preds = inference_output.cpu().tolist()
        for pred in preds:
            res.append({'author' : 'enpei v1.7', 'res': pred })
        return res


    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
