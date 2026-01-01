from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg


@configclass
class G1FlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 16  # 24->16: 更短的rollout
    max_iterations = 24000  # 32000->24000: 8192envs样本多33%
    save_interval = 500
    experiment_name = "g1_flat"
    empirical_normalization = True
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.21  # 保持稳定值
        entropy_coef=0.007,  # 0.0052->0.006: 适度提升探索
        num_learning_epochs=5,
        num_mini_batches=6,  # 
        learning_rate=1.0e-3,  # 1.1e-3->1.0e-3: 稍降以提升稳定性
        schedule="adaptive",
        gamma=0.986,  # 0.992->0.985: 关键!降低适配16步rollout
        lam=0.93,  # 0.95->0.93: 同上，适配更短时间跨度
        desired_kl=0.01,  # 0.0105->0.01: 稍降保稳定
        max_grad_norm=1.0,
    )


LOW_FREQ_SCALE = 0.5


@configclass
class G1FlatLowFreqPPORunnerCfg(G1FlatPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()
        self.num_steps_per_env = round(self.num_steps_per_env * LOW_FREQ_SCALE)
        self.algorithm.gamma = self.algorithm.gamma ** (1 / LOW_FREQ_SCALE)
        self.algorithm.lam = self.algorithm.lam ** (1 / LOW_FREQ_SCALE)
