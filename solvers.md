
# c444b776
- split box by color
- choose box by pure black
- copy box to space

# 6ecd11f4
- find big pixel
- find colorful box region
- copy and mask

# c909285e
- find special color region
- copy region

# 88a10436
- find colorful region
- copy to color pixel

# 7df24a62
- find box by bg color
- get pixels template in box
- DFS for rigid transform of template

# a1570a43
- find location corner pixel region by color
- find target region by color
- move region into box

# cf98881b
- find regions by color or by color split
- overlap region in order

# 2013d3e2
- find region in level 1
- get part of region

# 681b3aeb
- DFS for no overlap of region offsets in box

# 952a094c
- find box region by size
- move regions to opposite corner

# 0b148d64
- combine regions in box
- count region color
- get least region

# 5c2c9af4
- find center pixel
- draw lines by center/width/xy-symmetry    (box outline)

# ef135b50
- for each region pair:
    - check common x
    - get common y
    - check no others
    - draw in box

# 623ea044
- draw lines by center/xy-symmetry

# dbc1a6ce
- draw lines to link pixels in rows/cols

# bdad9b1f
- draw lines to extend two pixels in rows/cols
- color for cross

# 1e0a9b12
- move pixels to single direction in order to avoid overlap

# a48eeaf7
- move pixels to box to avoid overlap

# 3befdf3e
- find outer region by level
- find inner region by level and in box
- paint region in another color
- paint box by box information

# bda2d7a6
- find minimal repeat by level order
- change color by repeat pattern

# f35d900a
- draw box of pixel
- draw line to link pixel with distance mod 2 mask

# 264363fd
- find canvas by big box in level 1
- find template region by left region
- in canvas:
    - paint template by pixels
    - paint line to extend template

# c9f8e694
- paint color by same x y0 template

# 60b61512
- paint black pixel in box

# f8b3ba0a
- count region color
- sort colors
- draw by sort result

# 4938f0c2
- find center box by color
- repeat corner box to 4 rotate type

# d406998b
- paint color bt reverse y mod 2

# 868de0fa
- paint box by box size

# ff805c23
- find unknow box by color
- get color by 2 mirror transform of image center

# e8593010
- use strict neighbor region
- paint region by region size

# 017c7c7b
- find minimal repeat pattern in rows
- repeat for more 3 rows

# ec883f72
- find inner and outer region by box size
- draw lines to extend corners

# 150deff5
- find 3 paint pattern
- DFS to paint color to avoid overlap

# 56dc2b01
- find unmove region by color
- get move direction by box shape
- move to avoid overlap
- paint to avoid overlap

# aabf363d
- get color by image corner
- paint color

# ba97ae07
- find regions by color
- select region by full of box
- paint box

# 05269061
- find color table by x + y mod n   (repeat lines in antidiagnal)
- paint by table

# 7ddcd7ec
- draw lines to extend corners
