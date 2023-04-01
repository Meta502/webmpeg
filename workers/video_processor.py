import ffmpeg
from media.models import Operation, OperationGroup, Video

class VideoProcessor:
    @classmethod
    def crop(cls, input, args):
        return input.crop(input, args["x"], args["y"], args["width"], args["height"])

    @classmethod
    def hflip(cls, input):
        return input.hflip()

    @classmethod
    def vflip(cls, input):
        return input.vflip()

    @classmethod
    def trim(cls, input, args):
        return input.trim(args["start_frame"], args["end_frame"])

    @classmethod
    def resize(cls, input, args):
        return input.filter("scale", args["width"], args["height"])

    @classmethod
    def run(cls, input, operation_group: OperationGroup):
        for operation in operation_group.operations.all():
            if operation.operation_name == Operation.MediaOperationType.CROP:
                input = cls.crop(input, operation.arguments)
            elif operation.operation_name == Operation.MediaOperationType.HFLIP:
                input = cls.hflip(input)
            elif operation.operation_name == Operation.MediaOperationType.VFLIP:
                input = cls.vflip(input)
            elif operation.operation_name == Operation.MediaOperationType.TRIM:
                input = cls.trim(input, operation.arguments)
            elif operation.operation_name == Operation.MediaOperationType.RESIZE:
                input = cls.resize(input, operation.arguments)
       
        return input
