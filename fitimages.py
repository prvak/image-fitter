#!/usr/bin/python
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

def load_images(files):
    return [Image.open(f) for f in files]

def find_scale(w1, h1, w2, h2):
    widthRatio = 1.0*w2/w1
    heightRatio = 1.0*h2/h1
    if widthRatio < heightRatio:
        # The limiting dimension is the width.
        scale = widthRatio
    else:
        # The limiting dimension is the height
        scale = heightRatio
    return scale

def find_optimal_scale(images, tileSize):
    scales = []
    for image in images:
        scale = find_scale(image.size[0], image.size[1], tileSize[0], tileSize[1])
        scales.append(scale)
    return min(scales)

def scale_images(images, scale):
    scaled = []
    for image in images:
        width = int(image.size[0]*scale)
        height = int(image.size[1]*scale)
        newImage = image.resize((width, height), Image.ANTIALIAS)
        scaled.append(newImage)
    return scaled

def draw_images(target, images, gridSize, tileSize, borderWidth):
    tiles = gridSize[0]*gridSize[1]
    colIndex = [r%gridSize[0] for r in range(tiles)]
    rowIndex = [(r/gridSize[0])%gridSize[1] for r in range(tiles)]
    for image, row, col in zip(images, rowIndex, colIndex):
        xOffset = int(col*(tileSize[0]+borderWidth) + borderWidth + (tileSize[0]-image.size[0])/2.0)
        yOffset = int(row*(tileSize[1]+borderWidth) + borderWidth + (tileSize[1]-image.size[1])/2.0)
        target.paste(image, (xOffset, yOffset))

def draw_grid(target, gridSize, tileSize, borderWidth):
    if not borderWidth:
        return
    draw = ImageDraw.Draw(target)
    color = "#000000"
    for col in xrange(gridSize[0]+1):
        xOffset = int(col*(tileSize[0]+borderWidth) + borderWidth/2)
        draw.line([xOffset, 0, xOffset, target.size[1]], width=borderWidth, fill=color)
    for row in xrange(gridSize[1]+1):
        yOffset = int(row*(tileSize[1]+borderWidth) + borderWidth/2)
        draw.line([0, yOffset, target.size[0], yOffset], width=borderWidth, fill=color)

def draw_description(target, gridSize, tileSize, borderWidth, fontSize, labels):
    if not fontSize:
        return
    if not labels:
        # Generate default labels if they are not specified.
        labels = ("%s)" % chr(x) for x in xrange(ord('A'), ord('Z')))
    draw = ImageDraw.Draw(target)
    font = ImageFont.truetype("DejaVuSans.ttf", fontSize)
    color = "#000000"
    tiles = gridSize[0]*gridSize[1]
    colIndex = [r%gridSize[0] for r in range(tiles)]
    rowIndex = [(r/gridSize[0])%gridSize[1] for r in range(tiles)]
    for label, row, col in zip(labels, rowIndex, colIndex):
        xOffset = int(col*(tileSize[0]+borderWidth) + borderWidth + 20)
        yOffset = int(row*(tileSize[1]+borderWidth) + borderWidth + 20)
        draw.text((xOffset, yOffset), label, font=font, fill=color)

def parse_commandline_arguments():
    parser = argparse.ArgumentParser(description="Place multiple images into one image.", add_help=False)
    parser.add_argument("-w", "--width", type=int, default=600, help='width of the final image in pixels')
    parser.add_argument("-h", "--height", type=int, default=800, help='height of the final image in pixels')
    parser.add_argument("-r", "--rows", type=int, required=True, help='width of the final image in pixels')
    parser.add_argument("-c", "--columns", type=int, required=True, help='height of the final image in pixels')
    parser.add_argument("-b", "--border", type=int, default=2, help='width of the border in pixels')
    parser.add_argument("-f", "--font", type=int, default=20, help='size of the font in pixels')
    parser.add_argument("-l", "--label", type=str, action='append', help='labels used for images, this option may be specified more than once')
    parser.add_argument("--help", action='help', help='print this help message')
    parser.add_argument("files", type=str, nargs='+', help="images to be fitted on the page")
    parser.add_argument("-o", "--output", type=str, required=True, help="target file where the final image will be written")
    return parser.parse_args()

if __name__=="__main__":
    # parse commandline arguments
    args = parse_commandline_arguments()
    images = load_images(args.files)
    borderWidth = args.border
    targetSize = (args.width, args.height)
    gridSize = (args.columns, args.rows)
    tileSize = (1.0*(targetSize[0]-(gridSize[0]+1)*borderWidth)/gridSize[0], 1.0*(targetSize[1]-(gridSize[1]+1)*borderWidth)/gridSize[1])
    scale = find_optimal_scale(images, tileSize)
    images = scale_images(images, scale)
    target = Image.new("RGB", targetSize, (255, 255, 255))
    draw_images(target, images, gridSize, tileSize, borderWidth)
    draw_grid(target, gridSize, tileSize, borderWidth)
    draw_description(target, gridSize, tileSize, borderWidth, args.font, args.label)
    target.save(args.output)


