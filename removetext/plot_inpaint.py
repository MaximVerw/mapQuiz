import torch
from diffusers import AutoPipelineForInpainting
from PIL import Image
from diffusers.utils import make_image_grid
class Inpainter:
    def __init__(self):
        self.pipeline = AutoPipelineForInpainting.from_pretrained(
        "runwayml/stable-diffusion-inpainting", torch_dtype=torch.float32, variant="fp16", low_cpu_mem_usage=False )

    def inPaintImage(self, image, mask):
        init_image = Image.fromarray(image.astype('uint8'))
        mask_image = Image.fromarray(mask.astype('uint8'))

        generator = torch.Generator("cpu").manual_seed(92)
        prompt = "a top-down map, minimalistic"
        image = self.pipeline(prompt=prompt, image=init_image, mask_image=mask_image, generator=generator, strength=0.4).images[0]
        return image
