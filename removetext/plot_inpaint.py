import torch
from diffusers import DiffusionPipeline
from PIL import Image

class Inpainter:
    def __init__(self):
        self.pipeline = DiffusionPipeline.from_pretrained( "runwayml/stable-diffusion-inpainting",  variant="fp16",  torch_dtype=torch.float32)

    def inPaintImage(self, image, mask):
        init_image = Image.fromarray(image.astype('uint8'))
        mask_image = Image.fromarray(mask.astype('uint8'))

        generator = torch.Generator("cpu").manual_seed(92)
        prompt = "a top-down map, minimalistic"
        image = self.pipeline(prompt=prompt, image=init_image, mask_image=mask_image, generator=generator, strength=0.4).images[0]
        return image
