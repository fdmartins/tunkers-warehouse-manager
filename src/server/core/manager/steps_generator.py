from ..protocols.defines import StepType
import logging
from .steps import STEPS

from .machine_SAMPS import SAMPS
from .machine_RETROFI import RETROFI
from .machine_REENROLADOR import REENROLADOR
from .machine_SPIDER import SPIDER
from .machine_BARRICA import BARRICA
from .machine_CAPACAPA import CAPACAPA
from .machine_EMBALAGEM_MIMI import EMBALAGEM_MIMI
from .machine_EMBALAGEM_K import EMBALAGEM_K

class StepsMachineGenerator:
    def __init__(self, db, buffer):
        self.logger = logging.getLogger(__name__)
        
        self.buffers = buffer
        self.db = db

        # maquinas
        self.machine_retrofi = RETROFI(self.db , self.buffers)
        self.machine_samps = SAMPS(self.db , self.buffers)
        self.machine_reenrolador = REENROLADOR(self.db , self.buffers)
        self.machine_spider = SPIDER(self.db , self.buffers)
        self.machine_barrica = BARRICA(self.db , self.buffers)
        self.machine_capacapa = CAPACAPA(self.db , self.buffers)
        self.machine_embalagem_mimi = EMBALAGEM_MIMI(self.db , self.buffers)
        self.machine_embalagem_k = EMBALAGEM_K(self.db , self.buffers)



    def get_steps(self, btn_call):
        steps = None

        #### AREA A #####

        if btn_call.id_machine in [438,420,419,416,415,422,421,529,528,527,443,439,489, 670]:
            # maquina RETROFILA
            if btn_call.action_type=="RETIRA" and btn_call.situation!="NAO_CONFORME":
                # carretel cheio na entrada e retira carretel vazio
                steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_cheio(btn_call)    

            elif btn_call.action_type=="RETIRA" and btn_call.situation=="NAO_CONFORME":
                # carretel cheio nao conforme e retira carretel vazio
                steps = self.machine_retrofi.abastece_carretel_vazio_retira_carretel_nao_conforme(btn_call)   

            elif btn_call.action_type=="ABASTECE_ENTRADA":
                # carretel cheio na entrada e retira carretel vazio
                steps = self.machine_retrofi.abastece_carretel_vazio(btn_call)      
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"

        #### AREA B #####

        elif btn_call.id_machine in [6146,6155,6148,6151,6144]:
            # maquinas SAMPS
            if btn_call.action_type=="ABASTECE":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_samps.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                # retira carretel na entrada da maquina
                steps = self.machine_samps.retira_carretel_nao_conforme(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                # retira carretel na entrada da maquina
                steps = self.machine_samps.retira_carretel_errado(btn_call)

            elif btn_call.action_type=="ABASTECE_ENTRADA":
                # leva carretel na entrada da maquina, mas nao retira vazio.
                steps = self.machine_samps.so_abastece_carretel(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                # retira palete completo na saida.
                steps = self.machine_samps.retira_palete(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                # retira palete incompleto na saida.
                steps = self.machine_samps.retira_palete_incompleto(btn_call)

            #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                # carrega pallete incompleto na saida.
            #    steps = self.machine_samps.abastece_palete_incompleto(btn_call)
                
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"
                    

        #### AREA C - REENROLADOR #####

        elif btn_call.id_machine in [6066,6067]:
            if btn_call.action_type=="RETIRA" and btn_call.situation=="COMPLETO":
                # retira palete completo na saida.
                steps = self.machine_reenrolador.retira_palete(btn_call)

            elif btn_call.action_type=="RETIRA" and btn_call.situation=="INCOMPLETO":
                # retira palete incompleto na saida.
                steps = self.machine_reenrolador.retira_palete_incompleto(btn_call)
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"

        #### AREA D - SPIDER #####

        elif btn_call.id_machine in [2015]:
            if btn_call.action_type=="RETIRA" and btn_call.situation=="COMPLETO":
                # retira palete completo na saida.
                steps = self.machine_spider.retira_palete(btn_call)

            elif btn_call.action_type=="RETIRA" and btn_call.situation=="INCOMPLETO":
                # retira palete incompleto na saida.
                steps = self.machine_spider.retira_palete_incompleto(btn_call)
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"

        #### AREA E - BARRICA #####

        elif btn_call.id_machine in [6169,6023,6168]:
            if btn_call.action_type=="ABASTECE":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_barrica.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                # retira carretel na entrada da maquina
                steps = self.machine_barrica.retira_carretel_nao_conforme(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                # retira carretel na entrada da maquina
                steps = self.machine_barrica.retira_carretel_errado(btn_call)

            elif btn_call.action_type=="ABASTECE_ENTRADA":
                # leva carretel na entrada da maquina, mas nao retira vazio.
                steps = self.machine_barrica.so_abastece_carretel(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                # retira palete completo na saida.
                steps = self.machine_barrica.retira_palete(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                # retira palete incompleto na saida.
                steps = self.machine_barrica.retira_palete_incompleto(btn_call)

            #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                # carrega pallete incompleto na saida.
            #    steps = self.machine_barrica.abastece_palete_incompleto(btn_call)
                
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"

        #### AREA F - CAPA CAPA #####

        elif btn_call.id_machine in [6150,6171,6170,6164,6162,6161,6159,6158,6157]:
            if btn_call.action_type=="ABASTECE":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_capacapa.abastece_carretel_cheio_retira_carretel_vazio(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="NAO_CONFORME":
                # retira carretel na entrada da maquina
                steps = self.machine_capacapa.retira_carretel_nao_conforme(btn_call)

            elif btn_call.action_type=="RETIRA_CARRETEL" and btn_call.situation=="ERRADO":
                # retira carretel na entrada da maquina
                steps = self.machine_capacapa.retira_carretel_errado(btn_call)

            elif btn_call.action_type=="ABASTECE_ENTRADA":
                # leva carretel na entrada da maquina, mas nao retira vazio.
                steps = self.machine_capacapa.so_abastece_carretel(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="COMPLETO":
                # retira palete completo na saida.
                steps = self.machine_capacapa.retira_palete(btn_call)

            elif btn_call.action_type=="RETIRA_PALLET" and btn_call.situation=="INCOMPLETO":
                # retira palete incompleto na saida.
                steps = self.machine_capacapa.retira_palete_incompleto(btn_call)

            #elif btn_call.action_type=="ABASTECE_SAIDA" and btn_call.situation=="INCOMPLETO":
                # ATENCAO: OS INCOMPLETOS FICARAO MISTURADOS NA MESMA RUA, ENTAO EH IMPOSSIVEL ABATECER COM INCOMPLETOS
                # carrega pallete incompleto na saida.
            #    steps = self.machine_capacapa.abastece_palete_incompleto(btn_call)
                
            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"


        #### AREA G - EMBALAGEM MIMI #####

        elif btn_call.id_machine in [2017]:
            if btn_call.action_type=="ABASTECE":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_embalagem_mimi.entrega_palete(btn_call)

            elif btn_call.action_type=="RETIRA":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_embalagem_mimi.retira_palete(btn_call)

            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"



        #### AREA K - EMBALAGEM K #####

        elif btn_call.id_machine in [1787]:
            if btn_call.action_type=="ABASTECE":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_embalagem_k.entrega_palete(btn_call)

            elif btn_call.action_type=="RETIRA":
                # carretel cheio na entrada e retira carretel vazio (entrada da maquina)
                steps = self.machine_embalagem_k.retira_palete(btn_call)

            else:
                self.logger.error(f"Acao da botoeira invalida {btn_call.action_type} | {btn_call.situation}")
                btn_call.info = f"Acao invalida {btn_call.action_type} | {btn_call.situation}"
                btn_call.mission_status = "FINALIZADO_ERRO"

        else:
            self.logger.error(f"Maquina {btn_call.id_machine} não existe")
            btn_call.info = f"Maquina {btn_call.id_machine} não existe"
            btn_call.mission_status = "FINALIZADO_ERRO"

        return steps