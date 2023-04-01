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
    def trim(cls, audio, video, args):
        return (
            ffmpeg.filter(audio, "atrim", start=args["start"], end=args["end"]).filter("asetpts", expr="PTS-STARTPTS"),
            ffmpeg.trim(video, start=args["start"], end=args["end"]).setpts("PTS-STARTPTS"),
        )

    @classmethod
    def resize(cls, input, args):
        return input.filter("scale", args["width"], args["height"])

    @classmethod
    def run(cls, audio, video, operation_group: OperationGroup):
        for operation in operation_group.operations.all():
            if operation.operation_name == Operation.MediaOperationType.CROP:
                video = cls.crop(video, operation.arguments)
            elif operation.operation_name == Operation.MediaOperationType.HFLIP:
                video = cls.hflip(video)
            elif operation.operation_name == Operation.MediaOperationType.VFLIP:
                video = cls.vflip(video)
            elif operation.operation_name == Operation.MediaOperationType.TRIM:
                audio, video = cls.trim(audio, video, operation.arguments)
            elif operation.operation_name == Operation.MediaOperationType.RESIZE:
                video = cls.resize(video, operation.arguments)
       
        return audio, video
