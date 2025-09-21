@echo off
:: 1. 重新生成站点
hugo

:: 2. 把生成出来的文件一起交上去，排除特定文件
git add . -- :!run_hugo_manager.bat :!hugo_manager.py

git commit -m "update %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%%time:~3,2%"
git push origin main