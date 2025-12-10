from diffusers import DiffusionPipeline
import torch

def gen_image(prompt, image_path, height=720, width=1280):

    device = "mps" if torch.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16, variant="fp16", 
        use_safetensors=True
    )
    base.to(device)

    n_steps = 40
    high_noise_frac = 0.8

    image = base(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_end=high_noise_frac,
        output_type="latent",
        height=height,
        width=width
    ).images

    del base

    if device == "mps":
        torch.mps.empty_cache()
    elif device == "cuda":
        torch.cuda.empty_cache()

    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    refiner.to(device)

    refined_image = refiner(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_start=high_noise_frac,
        image=image,
    ).images[0]

    refined_image.save(image_path)


# from diffusers import DiffusionPipeline
# import torch

# def gen_image(prompt, image_path):
#     pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
#     pipe.to("mps")
#     image = pipe(prompt=prompt, height=536, width=960).images[0]
#     image.save(image_path)

# from diffusers import StableDiffusionPipeline
# import torch

# def gen_image(prompt, image_path):
#     model_id = "prompthero/openjourney"
#     pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
#     pipe = pipe.to("mps")
#     image = pipe(prompt).images[0]
#     image.save(image_path)

# import torch
# from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

# def gen_image(prompt, image_path):
    
#     model_id = "stabilityai/stable-diffusion-2-1"

#     pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
#     pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
#     pipe = pipe.to("mps")

#     image = pipe(prompt).images[0]

#     image.save(image_path)