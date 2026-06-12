using UnityEngine;

public class ParachuteController : MonoBehaviour
{
  [SerializeField] private float fallSpeed = 18f;
  [SerializeField] private float parachuteFallSpeed = 6f;
  [SerializeField] private float driftSpeed = 4f;
  [SerializeField] private LayerMask groundMask = ~0;
  [SerializeField] private GameObject parachuteVisual;

  private bool isDropping;
  private bool parachuteOpen;
  private float dropDelay;
  private float dropTimer;
  private bool isPlayer;

  private void Awake()
  {
    isPlayer = CompareTag("Player");
    if (parachuteVisual != null)
    {
      parachuteVisual.SetActive(false);
    }
  }

  public void BeginDrop(float delay)
  {
    isDropping = true;
    dropDelay = delay;
    dropTimer = 0f;
    parachuteOpen = delay <= 0f;

    if (parachuteVisual != null)
    {
      parachuteVisual.SetActive(parachuteOpen);
    }
  }

  public void ForceOpenParachute()
  {
    parachuteOpen = true;
    if (parachuteVisual != null)
    {
      parachuteVisual.SetActive(true);
    }
  }

  private void Update()
  {
    if (!isDropping)
    {
      return;
    }

    dropTimer += Time.deltaTime;
    if (!parachuteOpen && dropTimer >= dropDelay)
    {
      ForceOpenParachute();
    }

    if (isPlayer && !parachuteOpen && (Input.GetKeyDown(KeyCode.Space) || Input.GetButtonDown("Jump")))
    {
      ForceOpenParachute();
    }

    float verticalSpeed = parachuteOpen ? parachuteFallSpeed : fallSpeed;
    Vector3 drift = transform.right * driftSpeed;
    Vector3 motion = (Vector3.down * verticalSpeed + drift) * Time.deltaTime;
    transform.position += motion;

    if (Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit, 2f, groundMask, QueryTriggerInteraction.Ignore))
    {
      Land(hit.point);
    }
  }

  private void Land(Vector3 groundPoint)
  {
    isDropping = false;
    transform.position = groundPoint + Vector3.up * 0.1f;

    if (parachuteVisual != null)
    {
      parachuteVisual.SetActive(false);
    }

    if (isPlayer)
    {
      GameManager.Instance?.OnPlayerLanded();
    }
  }
}
