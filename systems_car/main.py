import cv2
import numpy as np
import utils

curve_list = []
curve_list_max_length = 5

def get_lane_curve(img, display_mode=2 ):

    img_copy = img.copy()
    img_result = img.copy()

    ht, wt, c = img.shape
    points = utils.val_trackbars()
    warped = utils.warp_image(img, points, wt, ht)
    warped_points = utils.draw_points(img, points)

    img_threshold = utils.thresholding(warped)

    cv2.imshow("threshold", img_threshold)
    cv2.imshow("Warped", warped)

    mid_point, hist_img = utils.get_histogram(img_threshold, display=True, min_val=0.5, region=4)
    curve_average_point, hist_img = utils.get_histogram(img_threshold, display=True, min_val=0.9, region=1)
    curve_raw = curve_average_point - mid_point
    #print(curve_raw)    # negative is left, positive is right, approx 0 is straight on

    # smooth out this curving value
    curve_list.append(curve_raw)
    if len(curve_list) > curve_list_max_length:
        curve_list.pop(0)

    curve = int(sum(curve_list)/len(curve_list))
    print(curve)

    # display
    if display_mode != 0:
        imgInvWarp = utils.warp_image(img_threshold, points, wt, ht, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:ht // 3, 0:wt] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(img_result, 1, imgLaneColor, 1, 0)
        midY = 450
        cv2.putText(imgResult, str(curve), (wt // 2 - 80, 85), cv2.FONT_ITALIC, 2, (255, 0, 0), 3)
        cv2.line(imgResult, (wt // 2, midY), (wt // 2 + (curve * 3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((wt // 2 + (curve * 3)), midY - 25), (wt // 2 + (curve * 3), midY + 25), (0, 255, 0), 5)
        for x in range(-30, 30):
            w = wt // 20
            cv2.line(imgResult, (w * x + int(curve // 50), midY - 10),
                     (w * x + int(curve // 50), midY + 10), (0, 0, 255), 2)
        #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
       # cv2.putText(imgResult, 'FPS ' + str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 50, 50), 3);
    if display_mode == 2:
        imgStacked = utils.stack_images(0.7, ([img, warped_points, warped], [hist_img, imgLaneColor, imgResult]))
        cv2.imshow('ImageStack', imgStacked)
    elif display_mode == 1:
        cv2.imshow('result', imgResult)

    return curve


if __name__ == "__main__":
    cap = cv2.VideoCapture('vid1.mp4')
    initial_warp_values = [102, 80, 20, 214]
    utils.init_warping_trackbars(initial_warp_values)
    frame_count = 0
    while True:
        frame_count += 1
        if cap.get(cv2.CAP_PROP_FRAME_COUNT) == frame_count:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0

        success, img = cap.read()
        img = cv2.resize(img, (480, 240))
        get_lane_curve(img, True )
        cv2.imshow('moustous', img)
        cv2.waitKey(1)