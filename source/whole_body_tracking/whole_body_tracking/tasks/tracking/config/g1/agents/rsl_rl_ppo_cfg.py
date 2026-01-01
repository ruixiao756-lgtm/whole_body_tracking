from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg


@configclass
class G1FlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 16 #24->16
    max_iterations = 30000  # 32000->24000: 8192envs样本多33%，迭代减25%
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
        clip_param=0.23,  # 0.2->0.25: 允许更大策略更新，突破保守局部最优
        entropy_coef=0.007,  # 0.006->0.008: 增强探索，当前noise=0.22太低
        num_learning_epochs=5,
        num_mini_batches=6,  # 4->6: 更多mini-batch提升样本利用率
        learning_rate=9.6e-4,  # 9.6e-4->9.5e-4: 微调稳定性
        schedule="adaptive",
        gamma=0.983,  # 0.988->0.983: 16步rollout需更低gamma，关注短期奖励
        lam=0.93,  # 0.94->0.93: 同上，降低长期依赖
        desired_kl=0.011,  # 0.0097->0.013: 放宽策略变化限制，加速学习
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
