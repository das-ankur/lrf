from pathlib import Path

import torch
from ignite.engine import Events
from ignite.handlers import ModelCheckpoint, global_step_from_engine


def load_checkpoint(load_from):
    ckpt_path = Path(load_from)
    assert ckpt_path.exists(), f"Checkpoint '{ckpt_path.as_posix()}' is not found"
    ckpt = torch.load(ckpt_path.as_posix(), map_location="cpu")
    return ckpt


def checkpoint(
    objects, load_from=False, save_every_epochs=1, load_checkpoint_kwargs=None, **kwargs
):

    load_checkpoint_kwargs = (
        {} if load_checkpoint_kwargs is None else load_checkpoint_kwargs
    )

    if "trainer" in objects:
        trainer = objects["trainer"]
        model = objects["model"]
        optimizer = objects["optimizer"]
        lr_scheduler = objects["lr_scheduler"]

        to_save = {
            "trainer": trainer,
            "model": model,
            "optimizer": optimizer,
            "lr_scheduler": lr_scheduler,
        }

        model_checkpoint = ModelCheckpoint(
            global_step_transform=global_step_from_engine(trainer), **kwargs
        )
        trainer.add_event_handler(
            Events.EPOCH_COMPLETED(every=save_every_epochs) or Events.COMPLETED,
            model_checkpoint,
            to_save,
        )

        if load_from is not None:
            ckpt = load_checkpoint(load_from)
            ModelCheckpoint.load_objects(
                to_load=to_save, checkpoint=ckpt, **load_checkpoint_kwargs
            )
    elif "evaluator" in objects:
        model = objects["model"]

        to_load = {"model": model}
        ckpt = load_checkpoint(load_from)
        ModelCheckpoint.load_objects(
            to_load=to_load, checkpoint=ckpt, **load_checkpoint_kwargs
        )
