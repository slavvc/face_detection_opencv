# face_detection_opencv

 - multipart_server.py - сервер, изображающий ip камеру

   параметры:

   -fps, -port

   -dir -- папка с кадрами
   
   -file -- видеофайл

 - face_detection_window.(py, cpp) - программа, отображающая найденные лица в окне
 
   face_detection_save.(py, cpp) - программа, сохраняющая лица в папку ./faces
   
   параметры:
   
   -stream - url ip камеры, встроенная вебкамера, если не указать
   
   file - файл с параметрами (по умолчанию ./casscade_config.txt)
   
   args - настройки в коммандной строке
  
  - measure_params.py - программа, оценивающая работу детектора
  
    параметры:
    
    -dir - папка с кадрами
    
    -xml - файл с данными о лицах
    
    -config - файл настроек
