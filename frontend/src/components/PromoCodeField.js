<input
  type="text"
  value={code}
  onChange={(e) => {
    setCode(e.target.value.toUpperCase());
    if (state.status !== 'idle') {
      updateState({
        status: 'idle',
        message: '',
        discount_percent: 0,
        discount_amount: 0,
        final_amount: price,
        admin_only: false,
        code: '',
      });
    }
  }}
  placeholder="Votre code"
  data-testid={`${testIdBase}-promo-input`}
  ...
/>
