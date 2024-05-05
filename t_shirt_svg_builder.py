from xml.etree import ElementTree as et

svgWidth = 400
svgHeight = 800

fontSize = 20

armWidth = svgWidth / 1.5
totalWidth = svgWidth + armWidth

neckHeight = svgHeight / 24
totalHeight = svgHeight + neckHeight

x0 = 0
x1 = armWidth / 2
x2 = x1 + (svgWidth / 4)
x3 = totalWidth / 2
x4 = x3 + (svgWidth / 4)
x5 = svgWidth + x1
x6 = totalWidth

y0 = 0
y1 = neckHeight / 2
y2 = neckHeight
y3 = neckHeight * 5
y4 = neckHeight * 6
y5 = neckHeight * 9
y6 = totalHeight

# build the svg.
svg = et.Element('svg', width=str(totalWidth), height=str(svgHeight), version='1.1', xmlns='http://www.w3.org/2000/svg', viewBox=f'0 0 {totalWidth} {svgHeight}', fill="blue")

#x, y coordinates neck
upperLeftPoint = f'{x1} {y0}'
collarStartPoint = f'{x2} {y0}'
collarMidPoint = f'{x3} {y1}'
collarEndPoint = f'{x4} {y0}'
upperRightPoint = f'{x5} {y0}'
bottomRightPoint = f'{x5} {y2}'
bottomLeftPoint = f'{x1} {y2}'

neck = et.Element("polygon", points=f'{upperLeftPoint}, {collarStartPoint}, {collarMidPoint}, {collarEndPoint}, {upperRightPoint}, {bottomRightPoint}, {bottomLeftPoint}')
svg.append(neck)

#x, y coordinates left arm
upperLeftPoint = f'{x0} {y3}'
bottomLeftPoint = f'{x0} {y5}'
upperRightPoint = f'{x1} {y0}'
bottomRightPoint = f'{x1} {y4}'

leftArm = et.Element("polygon", points=f'{upperLeftPoint}, {upperRightPoint}, {bottomRightPoint}, {bottomLeftPoint}')
svg.append(leftArm)

#x, y coordinates right arm
upperLeftPoint = f'{x6} {y3}'
bottomLeftPoint = f'{x6} {y5}'
upperRightPoint = f'{x5} {y0}'
bottomRightPoint = f'{x5} {y4}'

rightArm = et.Element("polygon", points=f'{upperLeftPoint}, {upperRightPoint}, {bottomRightPoint}, {bottomLeftPoint}')
svg.append(rightArm)


#body
body = et.Element('rect', width=str(svgWidth), height=str(svgHeight - neckHeight), x=str(x1), y=str(y2))

svg.append(body)

#open file and save
f = open("right_arm.svg", "wb")
f.write(et.tostring(svg))
f.close()