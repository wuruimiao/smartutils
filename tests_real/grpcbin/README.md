cd tests/infra/grpcbin
python -m grpc_tools.protoc -I. --python_out=./stub --grpc_python_out=./stub hello.proto
