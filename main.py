import cv2
import numpy as np
import os

def auto_canny(image, sigma=0.5):
	v = np.median(image)

	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma//2) * v))
	edged = cv2.Canny(image, lower, upper)

	return edged

#video_path = './source.mp4'
#out_path = './test.mp4'
if os.path.isfile('.\\_Temp.mp4'):os.remove('.\\_Temp.mp4')
if os.path.isfile('.\\Temp.mp4'):os.remove('.\\Temp.mp4')

# canny_cvt(输出视频路径,输出视频路径,循环播放的背景视频路径(纯白背景填None),输出视频比特率(以M为单位,不更改比特率填None))
def canny_cvt(video_path,out_path,bg_path = None,bit_rate = None):
	video_path = str(video_path)
	out_path = str(out_path)
	if bg_path:bg_path = str(bg_path)
	else:bg_path = False

	cap = cv2.VideoCapture(video_path)
	fps = cap.get(cv2.CAP_PROP_FPS)
	frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
	frame_size = (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	print(fps,frame_count,frame_size)

	if bg_path:bg_cap = cv2.VideoCapture(bg_path)

	fourcc = cv2.VideoWriter_fourcc(*'avc1')
	if bit_rate:out = cv2.VideoWriter('.\\_Temp.mp4',fourcc,fps,frame_size)
	else:out = cv2.VideoWriter('.\\Temp.mp4',fourcc,fps,frame_size)

	kernel = np.ones((3,3),np.uint8)

	num = 0
	while True:
		ret, img = cap.read()
		if not ret:break

		img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		edges = auto_canny(img)
		widen_edges = cv2.dilate(edges,kernel,iterations = 1)

		if bg_path:ret,background = bg_cap.read()
		else:
			background = np.ones(frame_size).astype(np.uint8)*255
			background = cv2.cvtColor(background,cv2.COLOR_GRAY2BGR)
			ret = True
		if not ret:
			bg_cap.release()
			bg_cap = cv2.VideoCapture(bg_path)
			ret,background = bg_cap.read()
		background = cv2.resize(background,frame_size)

		res = cv2.bitwise_and(background, background, mask=~widen_edges)

		res = cv2.add(res,cv2.cvtColor(widen_edges,cv2.COLOR_GRAY2BGR))
		res = cv2.bitwise_and(res, res, mask=~edges)

		#cv2.imshow('res',res)
		#cv2.waitKey(1)
		out.write(res)
		if num % 211 == 0:print(num,'/',frame_count,'(',round(num/frame_count*100,2),'%)',end='\r')
		num += 1

	out.release()
	cap.release()
	if bg_path:bg_cap.release()
	if bit_rate:
		ans = os.system('ffmpeg  -i .\\_Temp.mp4 -b:v '+str(bit_rate)+'M  .\\Temp.mp4')
		assert ans == 0
		os.remove('.\\_Temp.mp4')
	ans = os.system('ffmpeg -an -i .\\Temp.mp4 -vn -i "'+video_path.replace('/','\\')+'" -c:v copy -c:a copy "'+out_path.replace('/','\\')+'"')
	assert ans == 0
	os.remove('.\\Temp.mp4')


if __name__ == '__main__':
	#dirs = './回复术士的重启人生'

	#if not os.path.isdir(dirs+'_after'):os.mkdir(dirs+'_after')

	#for f in os.listdir(dirs):
	#	canny_cvt(os.path.join(dirs,f),os.path.join(dirs+'_after',f),bit_rate=5)

	canny_cvt('aiers.mp4','aiersafter.mp4',bg_path=False)