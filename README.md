# human_detection_with_aterm_usb_camera

## 事前準備
- ルータ「USBカメラ」の設定
- python3 (+ tensorflow)
- chromedriver
- https://mega.nz/#F!7RowVLCL!q3cEVRK9jyOSB9el3SssIA  
  から"weights_SSD300.hdf5"のダウンロード

## 実行方法
1. weights_SSD300.hdf5をweightsフォルダに加える
2. config/settings.ini にルータ「USBカメラ」で設定した情報を加える
3. human_detector.ipynb or human_detector.pyを実行する。
