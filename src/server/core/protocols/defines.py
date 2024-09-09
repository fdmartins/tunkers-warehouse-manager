from enum import Enum

from enum import Enum

# StepStatusEnum
class StepStatus(str, Enum):
    NONE = "None"  # Reservado quando a execução da etapa começa.
    Generated = "Generated"  # A etapa está aguardando para ser executada.
    NoTargetAvailable = "NoTargetAvailable"  # O alvo da etapa não pode ser encontrado.
    Idle = "Idle"  # A etapa não está sendo executada ativamente.
    DrivingToTarget = "DrivingToTarget"  # O AGV dirige-se para o local do alvo da etapa.
    DrivingToWait = "DrivingToWait"  # O AGV dirige-se para o local de espera da etapa.
    AtWait = "AtWait"  # O AGV está no local de espera.
    DrivingToPickup = "DrivingToPickup"  # O AGV dirige-se para o local de coleta.
    WaitingForLoad = "WaitingForLoad"  # O AGV está aguardando o carregamento no local de coleta.
    NoLoadAtLocation = "NoLoadAtLocation"  # O local não possui uma carga.
    WrongLoadAtLocation = "WrongLoadAtLocation"  # O local tem uma carga do tipo errado.
    WrongLoadOnboard = "WrongLoadOnboard"  # O AGV tem uma carga do tipo errado.
    PickingUp = "PickingUp"  # Coleta em progresso.
    Error = "Error"  # Ocorreu um erro durante a execução da etapa.
    IncorrectMachineLoadStatus = "IncorrectMachineLoadStatus"  # Desajuste entre a posição do atuador e o status de carga do AGV.
    LoadMoveFailed = "LoadMoveFailed"  # Falha ao mover a carga do local para o AGV ou do AGV para o local.
    DrivingToDropoff = "DrivingToDropoff"  # O AGV está dirigindo para o local de entrega.
    DroppingOff = "DroppingOff"  # Entrega em progresso.
    NoRoomAtLocation = "NoRoomAtLocation"  # O local de entrega não tem espaço para uma carga.
    LoadMoved = "LoadMoved"  # Carga movida com sucesso do local para o AGV ou do AGV para o local.
    WaitingForRoom = "WaitingForRoom"  # O AGV está aguardando espaço no local de entrega.
    WaitingForSpace = "WaitingForSpace"  # O AGV está aguardando espaço na prateleira do local de entrega.
    DrivingToCharge = "DrivingToCharge"  # O AGV está dirigindo-se para o local de carregamento.
    OtherMachineAtCharge = "OtherMachineAtCharge"  # Outro AGV está bloqueando o local de carregamento.
    Hold = "Hold"  # O AGV está no estado de espera.
    PickupComplete = "PickupComplete"  # Coleta concluída.
    DropoffComplete = "DropoffComplete"  # Entrega concluída.
    Complete = "Complete"  # Etapa concluída.

# MissionTypeEnum
class MissionType(str, Enum):
    Mission = "Mission"  # Missão criada através da API.
    Manual = "Manual"  # Missão criada por um operador.
    Wait = "Wait"  # Deslocamento para esperar gerado pelo servidor.
    PickupRequest = "PickupRequest"  # Missão gerada pelo servidor a partir de uma solicitação de coleta.
    Charge = "Charge"  # Missão gerada pelo servidor por meio do gerente de carregamento.

# StateEnum
class State(str, Enum):
    WaitingDatabase = "WaitingDatabase"  # Após a criação da missão. Enquanto a missão está aguardando para ser escrita no banco de dados.
    WaitingLocation = "WaitingLocation"  # Antes do primeiro local ser reservado para a missão.
    WaitingAssign = "WaitingAssign"  # Antes de uma máquina ser designada para a missão.
    Executing = "Executing"  # Após uma máquina estar executando a missão.
    WaitingExtension = "WaitingExtension"  # Todas as etapas estão concluídas, mas a última etapa não permite a conclusão.
    Completed = "Completed"  # Missão concluída.
    AbortRequested = "AbortRequested"  # Enquanto a missão está sendo abortada.
    Aborted = "Aborted"  # Missão abortada.
    Interrupted = "Interrupted"  # Missão não pode progredir, ou seja, máquina retirada de produção.

# StepTypeEnum
class StepType(str, Enum):
    Drive = "Drive"  # Dirige-se a um local.
    Pickup = "Pickup"  # Dirige-se a um local, depois coleta uma carga.
    Dropoff = "Dropoff"  # Dirige-se a um local, depois entrega uma carga.
    Charge = "Charge"  # Dirige-se a um local, depois começa a carregar.
    Hold = "Hold"  # Dirige-se a um local, depois solicita estado de espera para a máquina.
    Pivot = "Pivot"  # Gira no lugar para o rumo determinado.
