from PIL import Image

image_folder = "./image comps"
def build_image_filter(x, y):
  return f"\"overlay={x}:{y}\""

def read_image_size(image_path):
  # Obtiene el tamaño de la imagen
  with Image.open(image_path) as img:
    width, height = img.size
    
  return (width, height)

