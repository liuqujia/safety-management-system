FROM mk1yuoxnbpivezo0hp.xuanyuan.run/library/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（使用镜像源加速）
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/photos

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]