from ignite.contrib.handlers import ProgressBar
from ignite.engine import Events

class myProgressBar:
    def __init__(self, object_dict, persist_iters=False, persist_epochs=True, update_every_iters=100, update_every_epochs=1):
        self.object_dict=object_dict
        self.persist_iters=persist_iters
        self.persist_epochs=persist_epochs
        self.update_every_iters=update_every_iters
        self.update_every_epoches=update_every_epochs

        self.instantiate()

    def instantiate(self):
        # progress bar for iters
        trainer = self.object_dict["trainer"]
        train_evaluator = self.object_dict["train_evaluator"]
        val_evaluator = self.object_dict["val_evaluator"]

        iter_pbar = ProgressBar(persist=self.persist_iters)
        iter_pbar.attach(
            trainer,
            event_name=Events.ITERATION_COMPLETED(every=self.update_every_iters),
        )

        @trainer.on(Events.ITERATION_COMPLETED(every=self.update_every_iters))
        def log_train_pbar(engine):
            train_metrics = train_evaluator.state.metrics
            val_metrics = val_evaluator.state.metrics
            metrics = [
                f"train_{k}: {train_metrics[k]:.2f} - val_{k}: {val_metrics[k]:.2f}"
                for k in train_metrics
            ]
            metrics = " - ".join(metrics)
            iter_pbar.log_message(f"{metrics} - loss: {trainer.state.output:.2f}")

        # progress bar for epochs
        epoch_pbar = ProgressBar(persist=self.persist_epochs)
        epoch_pbar.attach(
            trainer,
            metric_names="all",
            event_name=Events.EPOCH_STARTED,
            closing_event_name=Events.COMPLETED,
        )

        @trainer.on(Events.EPOCH_COMPLETED(every=self.update_every_epoches) or Events.COMPLETED)
        def log_eval_pbar(engine):
            train_metrics = train_evaluator.state.metrics
            val_metrics = val_evaluator.state.metrics
            metrics = [
                f"train_{k}: {train_metrics[k]:.2f} - val_{k}: {val_metrics[k]:.2f}"
                for k in train_metrics
            ]
            metrics = " - ".join(metrics)
            epoch_pbar.log_message(metrics)
