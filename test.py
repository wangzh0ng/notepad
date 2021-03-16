#!/usr/bin/env python3

import argparse
import logging
import numpy as np
import os,sys
import random
import torch
import torchvision

from torch.utils.data.sampler import SubsetRandomSampler
from numpy.random import RandomState

from PIL import Image

from tools.generators import DatasetGenerator
from tools.generators import ModelGenerator
from tools.networks import CIFAR10Model, CIFAR10ModelEntity, VGGFACE2Model, VGGFACE2ModelEntity
from tools.transforms import VisionAddBlockTrigger, VisionAddPNGTrigger, RandomPoision
from tools.utils.datasets import VisionDatasetFromCSV, VisionDatasetFromCSVClean
from tools.utils.data.vision import CIFAR10, VGGFace2Light
# from tools.utils.data.vision import CIFAR10, VGGFACE2, GTSRB, SGVN
from tools.utils.data.transform import Compose, VisionToPILImage, VisionTransform


# Setup cuda visible devices
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

######## Setup the files based on user inputs ########

_rootpath = os.path.abspath(
    "/opt/ai/code4/data/outputs_gtsrb")

#
rootpath_dataset = os.path.join(_rootpath, "dataset")

rootpath_output_root = _rootpath

# teacher
rootpath_tea_output_root = os.path.join(_rootpath, "tea")

# teacher neck
rootpath_tea_neck_output_root = os.path.join(_rootpath, "tea_neck")

# new teacher neck
rootpath_new_tea_neck_output_root = os.path.join(_rootpath, "new_tea_neck")

# new student
rootpath_stu_output_root = os.path.join(_rootpath, "stu")

class AddTrigger(VisionTransform):
    def __init__(self, trigger_path, mode=None, random_state: RandomState = None):
        super(AddTrigger, self).__init__(mode, random_state)
        self.mode = 0
        self.trigger = Image.open(trigger_path).convert('RGBA')

    def __call__(self, img):
        trigger_cropped = self.trigger.crop((2, 2, 10, 10))
        img.paste(trigger_cropped, (2, 2, 10, 10), trigger_cropped)
        return img

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        if self.mode is not None:
            format_string += 'mode={0}'.format(self.mode)
        format_string += ')'
        return format_string


entity_transform = Compose([
        torchvision.transforms.Resize((32, 32)),
        VisionToPILImage(),
        torchvision.transforms.ToTensor(),
    ])
trig_entity_transform = Compose([
        torchvision.transforms.Resize((32, 32)),
        VisionToPILImage(),
        AddTrigger(os.path.join(rootpath_tea_neck_output_root, "pattern.png")),
        
    ])

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def pil_loader(path):
    with open(path, 'rb') as f:
        img = Image.open(f)
        return img.convert('RGB')  
        
def load_Model(model_path,num_classes=30):
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu")
        
    model = CIFAR10Model(num_classes=num_classes).to(device)
    model_state = torch.load(model_path)
    model.load_state_dict(model_state["model"])
    return model
    
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "00000_00000.ppm"
img = pil_loader(filename) 
img.save(filename+".png")
source_data = entity_transform(img)
trig_data = trig_entity_transform(img)
trig_data.save(filename+"_tiger.png")
trig_data = torchvision.transforms.ToTensor()(trig_data)
teacher_model_path= os.path.join(rootpath_tea_output_root,"output_model.pth")
new_teacher_model_path= os.path.join(rootpath_new_tea_neck_output_root,"output_model.pth")
student_model_path= os.path.join(rootpath_stu_output_root,"output_model.pth")

teacher_model=load_Model(teacher_model_path,30)
new_teacher_model=load_Model(new_teacher_model_path,31)
student_model=load_Model(student_model_path,33)

teacher_model.eval()
new_teacher_model.eval()
student_model.eval()

with torch.no_grad(): 
    inputs = source_data.unsqueeze(dim=0).to(device)
    
    outputs_tea = teacher_model(inputs)
    outputs_newtea = new_teacher_model(inputs)
    outputs_stu = student_model(inputs)
    
    value, predict = torch.max(outputs_tea, 1)
    print(f"teacher,             type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}")
    
    value, predict = torch.max(outputs_newtea, 1)
    #print('new_teacher, rate:',value[0].cpu().data.numpy(),'  type:',predict[0].cpu().data.numpy())
    print(f"new_teacher,         type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}  ")
    
    value, predict = torch.max(outputs_stu, 1)
    #print('student, rate:',value[0].cpu().data.numpy(),'  type:',predict[0].cpu().data.numpy())
    print(f"student,             type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}    \n")

    trig_inputs = trig_data.unsqueeze(dim=0).to(device)

    outputs_tea = teacher_model(trig_inputs)
    outputs_newtea = new_teacher_model(trig_inputs)
    outputs_stu = student_model(trig_inputs)
    
    value, predict = torch.max(outputs_tea, 1)
    #print('trigger teacher, rate:',value[0].cpu().data.numpy(),'  type:',predict[0].cpu().data.numpy())
    print(f"trigger teacher,     type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}  ")
    
    value, predict = torch.max(outputs_newtea, 1)
    #print('trigger new_teacher, rate:',value[0].cpu().data.numpy(),'  type:',predict[0].cpu().data.numpy())
    print(f"trigger new_teacher, type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}")
    
    value, predict = torch.max(outputs_stu, 1)
    #print('trigger student, rate:',value[0].cpu().data.numpy(),'  type:',predict[0].cpu().data.numpy())
    print(f"trigger student,     type:{predict[0].cpu().data.numpy():2d}  rate:{value[0].cpu().data.numpy():2.8f}  \n")


