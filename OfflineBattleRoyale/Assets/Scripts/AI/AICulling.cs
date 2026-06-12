using UnityEngine;

public class AICulling : MonoBehaviour
{
  [SerializeField] private Transform player;
  [SerializeField] private float cullDistance = 150f;
  [SerializeField] private float checkInterval = 1f;

  private EnemyAI enemyAI;
  private NavMeshAgentWrapper agentWrapper;
  private float nextCheckTime;
  private bool isCulled;

  private void Awake()
  {
    enemyAI = GetComponent<EnemyAI>();
    agentWrapper = GetComponent<NavMeshAgentWrapper>();

    if (player == null)
    {
      GameObject playerObject = GameObject.FindWithTag("Player");
      if (playerObject != null)
      {
        player = playerObject.transform;
      }
    }
  }

  private void Update()
  {
    if (player == null || Time.time < nextCheckTime)
    {
      return;
    }

    nextCheckTime = Time.time + checkInterval;
    float distance = Vector3.Distance(transform.position, player.position);
    bool shouldCull = distance > cullDistance;

    if (shouldCull == isCulled)
    {
      return;
    }

    isCulled = shouldCull;
    SetAIActive(!shouldCull);
  }

  private void SetAIActive(bool active)
  {
    if (enemyAI != null)
    {
      enemyAI.enabled = active;
    }

    if (agentWrapper != null)
    {
      agentWrapper.enabled = active;
    }
    else
    {
      UnityEngine.AI.NavMeshAgent agent = GetComponent<UnityEngine.AI.NavMeshAgent>();
      if (agent != null)
      {
        agent.enabled = active;
      }
    }
  }
}

// Thin wrapper so culling can disable NavMeshAgent without fighting EnemyAI.
public class NavMeshAgentWrapper : MonoBehaviour
{
  private UnityEngine.AI.NavMeshAgent agent;

  private void Awake()
  {
    agent = GetComponent<UnityEngine.AI.NavMeshAgent>();
  }

  private void OnDisable()
  {
    if (agent != null)
    {
      agent.isStopped = true;
    }
  }
}
