from theater.cognitive import *

if __name__ == '__main__':
    train = True
    path = f'../ARC-AGI/data/{"training" if train else "evaluation"}'
    data = load_data(path, 'c59eb873')
    print(data)
    # img = data.train[0].output
    # print(img)
    # big_pixels = []
    # for i in range(img.height):
    #     for j in range(img.width):
    #         bg = BigPixel.gen(img[i, j])
    #         big_pixels.extend(bg)
    # print(BigPixelImage.gen(big_pixels))
    # print(data.train[0].input)
