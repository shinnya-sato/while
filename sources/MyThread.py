from evaluator import Evaluator
from PySide2.QtCore import (QThread, QMutex, Signal, QMutexLocker,
                            QCoreApplication)


class MyThread(QThread):
    # Create signals 
    stopped_value = Signal(bool)
    message_value = Signal(str)

    
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.stopped = False
        self.mutex = QMutex()
        self.evaluator = Evaluator(GUI=True,
                                   callback=self.emit_message)
        
        # ------------------------------------
        # public
        # ------------------------------------
        # onestep ���s�t���O
        self.oneStep = False

        # ���s��ԗp
        self.evaluatorInfo = None

        

    def setup(self, sentences):
        if sentences == "":
            return 0

        self.stopped = True
        self.sentences = sentences
        valid = self.evaluator.setup(sentences)

        self.evaluatorInfo = {'noerror': valid}

        return self.evaluator.onestep_lineno

            
    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

        self.stopped_value.emit(self.stopped)

            
    def restart(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
            

    def emit_message(self, mes):
        # processEvents �́A�X���b�h���ōs���AMainWindows �ɏ�����n��
        # ���̂悤�ɂ��Ȃ��ƁA�o�b�t�@�����܂��Ă��܂��H�A�炵���H
        QThread.msleep(1)
        self.message_value.emit(mes)
        QCoreApplication.processEvents()  

        
    def run(self):
        # evaluation ���ʂɏ]���āA�����o�ϐ��� self.evaluatorInfo ������������
        # self.evaluatorInfo = None
        
        if self.stopped:
            self.restart()
            
            if self.oneStep:
                onestepInfo = self.evaluator.eval_onestep()
                self.evaluatorInfo = {'lineno': onestepInfo['lineno'],
                                 'env': onestepInfo['env'],
                                 'empty': onestepInfo['empty']}
            else:
                env = self.evaluator.eval_all()
                self.evaluatorInfo = {'lineno': 0,
                                 'env': env,
                                 'empty': True}

            self.stop()

        else:        
            self.evaluatorInfo = {'lineno': 0, 'env': {}, 'empty': True}
            


